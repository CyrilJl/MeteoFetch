from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List

import cfgrib
import pandas as pd
import requests
import xarray as xr

from ._misc import geo_encode_cf


class Model:
    """Classe de base pour le téléchargement et le traitement des données de modèles"""

    TIMEOUT = 20
    base_url_ = "https://object.data.gouv.fr/meteofrance-pnt/pnt"

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @classmethod
    def _download_file(cls, url: str) -> List[xr.Dataset]:
        """Télécharge un fichier GRIB à partir d'une URL et le charge en tant que liste de xarray.Dataset.

        Args:
            url (str): L'URL du fichier GRIB à télécharger.

        Returns:
            List[xr.Dataset]: Une liste de datasets xarray contenant les données du fichier GRIB.
                               Retourne une liste vide en cas d'erreur HTTP 404, propage les autres erreurs.

        Raises:
            requests.HTTPError: Pour les erreurs HTTP autres que 404.
        """
        try:
            with requests.get(url=url, timeout=cls.TIMEOUT) as response:
                response.raise_for_status()
                with TemporaryDirectory() as tmp_dir:
                    file_path = Path(tmp_dir) / "data.grib2"
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    datasets = cfgrib.open_datasets(
                        path=file_path,
                        indexpath="",
                        decode_timedelta=True,
                    )
                    processed_datasets = []
                    for ds in datasets:
                        processed_ds = cls._process_ds(ds).load()
                        processed_datasets.append(processed_ds)
                    return processed_datasets
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return []
            else:
                raise
        except Exception as _:
            raise

    @classmethod
    def _download_paquet(cls, date, paquet, variables, num_workers: int) -> Dict[str, xr.DataArray]:
        """Télécharge un paquet de données pour une date et un ensemble de variables spécifiques en parallèle.

        Args:
            date: La date pour laquelle télécharger les données.
            paquet: Le paquet de données à télécharger.
            variables: Les variables à extraire du paquet.
            num_workers (int): Le nombre de téléchargements parallèles à effectuer.

        Returns:
            Dict[str, xr.DataArray]: Un dictionnaire contenant les variables demandées sous forme de xarray.DataArray.
        """
        if isinstance(variables, str):
            variables_ = (variables,)
        else:
            variables_ = variables

        datasets = {}
        urls_to_download = [
            cls.base_url_ + "/" + cls.url_.format(date=date, paquet=paquet, group=group) for group in cls.groups_
        ]

        all_downloaded_datasets = []
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            results = executor.map(cls._download_file, urls_to_download)
            for dataset_list in results:
                all_downloaded_datasets.extend(dataset_list)

        if not all_downloaded_datasets:
            raise requests.HTTPError(f"No data files found or processed for date={date}, paquet={paquet}")

        for ds in all_downloaded_datasets:
            for field in ds.data_vars:
                if (variables_ is None) or (field in variables_):
                    if field not in datasets:
                        datasets[field] = []
                    datasets[field].append(ds[field])

        if variables_ is not None and not any(var in datasets for var in variables_):
            print(
                f"Warning: None of the requested variables {variables_} found in the downloaded data for date={date}, paquet={paquet}."
            )
            return {}

        if not datasets:
            print(f"Warning: No variables found in the downloaded data for date={date}, paquet={paquet}.")
            return {}

        final_datasets = {}
        for field in list(datasets.keys()):
            try:
                concatenated_da = xr.concat(datasets[field], dim="time").squeeze()
                concatenated_da["longitude"] = xr.where(
                    concatenated_da["longitude"] <= 180.0,
                    concatenated_da["longitude"],
                    concatenated_da["longitude"] - 360.0,
                    keep_attrs=True,
                )
                concatenated_da = concatenated_da.sortby("longitude")
                concatenated_da = concatenated_da.sortby("latitude")

                if "time" in concatenated_da.dims:
                    concatenated_da = concatenated_da.sortby("time")

                geo_encode_cf(da=concatenated_da)
                final_datasets[field] = concatenated_da
            except ValueError as e:
                print(f"Warning: Could not concatenate or process field '{field}'. Skipping. Error: {e}")
            except Exception as e:
                print(f"Warning: Unexpected error processing field '{field}'. Skipping. Error: {e}")

        return final_datasets

    @classmethod
    def check_paquet(cls, paquet):
        """Vérifie si le paquet spécifié est valide."""
        if paquet not in cls.paquets_:
            raise ValueError(f"paquet must be one of {cls.paquets_}")

    @classmethod
    def get_forecast(cls, date, paquet="SP1", variables=None, num_workers: int = 4) -> Dict[str, xr.DataArray]:
        """Récupère les prévisions pour une date et un paquet spécifiques, en parallèle.

        Args:
            date: La date pour laquelle récupérer les prévisions.
            paquet (str, optional): Le paquet de données à télécharger. Par défaut "SP1".
            variables (Optional[Union[str, List[str]]], optional): Les variables à extraire.
                                                                     Par défaut None (toutes variables).
            num_workers (int, optional): Nombre de téléchargements parallèles. Par défaut 4.

        Returns:
            Dict[str, xr.DataArray]: Un dictionnaire contenant les prévisions pour les variables demandées.
        """
        cls.check_paquet(paquet)
        date_dt = pd.to_datetime(str(date)).floor(f"{cls.freq_update}h")
        date_str = f"{date_dt:%Y-%m-%dT%H}"
        return cls._download_paquet(
            date=date_str,
            paquet=paquet,
            variables=variables,
            num_workers=num_workers,
        )

    @classmethod
    def get_latest_forecast(cls, paquet="SP1", variables=None, num_workers: int = 4) -> Dict[str, xr.DataArray]:
        """Récupère la dernière prévision disponible pour un paquet donné, en parallèle.

        Args:
            paquet (str, optional): Le paquet de données à télécharger. Par défaut "SP1".
            variables (Optional[Union[str, List[str]]], optional): Les variables à extraire.
                                                                    Par défaut None (toutes variables).
            num_workers (int, optional): Nombre de téléchargements parallèles. Par défaut 4.


        Returns:
            Dict[str, xr.DataArray]: Un dictionnaire contenant les prévisions pour les variables demandées.

        Raises:
            requests.HTTPError: Si aucune prévision n'est trouvée après plusieurs tentatives.
        """
        cls.check_paquet(paquet)
        latest_possible_date = pd.Timestamp.utcnow().floor(f"{cls.freq_update}h")

        max_attempts = 8

        for k in range(max_attempts):
            current_date = latest_possible_date - pd.Timedelta(hours=cls.freq_update * k)
            try:
                forecast_data = cls.get_forecast(
                    date=current_date,
                    paquet=paquet,
                    variables=variables,
                    num_workers=num_workers,
                )
                if forecast_data:
                    return forecast_data

            except requests.HTTPError as _:
                continue
            except Exception as _:
                continue

        raise requests.HTTPError(
            f"Pas de données touvées pour le paquet={paquet} parmi les {max_attempts} derniers runs."
        )


class HourlyProcess:
    @staticmethod
    def _process_ds(ds) -> xr.Dataset:
        ds = ds.expand_dims("valid_time").drop_vars("time").rename(valid_time="time")
        return ds


class MultiHourProcess:
    @staticmethod
    def _process_ds(ds) -> xr.Dataset:
        if "time" in ds:
            ds = ds.drop_vars("time")
        if "step" in ds.dims:
            ds = ds.swap_dims(step="valid_time").rename(valid_time="time")
        return ds
