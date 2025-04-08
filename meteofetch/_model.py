import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from shutil import copyfileobj
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
    past_runs_ = 8

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @classmethod
    def _url_to_file(cls, url: str, tempdir: TemporaryDirectory) -> Path:
        """Télécharge un fichier depuis une URL et le sauvegarde dans un répertoire temporaire.
        Meilleure gestion de la mémoire pour les fichiers volumineux.
        Utilise une taille de tampon de 16 Mo pour le téléchargement.
        """
        temp_path = Path(tempdir) / "temp.grib"

        with requests.get(url, stream=True, timeout=cls.TIMEOUT) as r:
            with open(temp_path, "wb") as f:
                copyfileobj(r.raw, f, length=1024 * 1024 * 16)
        return temp_path

    @classmethod
    def _download_file(cls, url: str, variables: List[str]) -> List[xr.DataArray]:
        try:
            with TemporaryDirectory(prefix="meteofetch_") as tempdir:
                temp_path = cls._url_to_file(url, tempdir)
                datasets = cfgrib.open_datasets(temp_path, backend_kwargs={"decode_timedelta": True, "indexpath": ""})

                dataarrays = []
                for ds in datasets:
                    for var in ds.data_vars:
                        if variables and var not in variables:
                            continue
                        if os.environ.get("meteofetch_test_mode") == "1":
                            dataarrays.append(ds[var].isnull(keep_attrs=True).load())
                        else:
                            dataarrays.append(ds[var].load())

                return dataarrays

        except Exception:
            return []

    @classmethod
    def _download_paquet(cls, date, paquet, variables, num_workers: int) -> Dict[str, xr.DataArray]:
        if isinstance(variables, str):
            variables_ = (variables,)
        else:
            variables_ = variables

        urls_to_download = [
            cls.base_url_ + "/" + cls.url_.format(date=date, paquet=paquet, group=group) for group in cls.groups_
        ]

        ret = {}

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            future_to_url = {executor.submit(cls._download_file, url, variables_): url for url in urls_to_download}

            for future in as_completed(future_to_url):
                dataarrays = future.result()
                for da in dataarrays:
                    if da.name not in ret:
                        ret[da.name] = []
                    ret[da.name].append(cls._process_ds(da))
                    del da

        for field in ret:
            ret[field] = xr.concat(ret[field], dim="time", coords="minimal", compat="override")
            ret[field] = geo_encode_cf(ret[field])
        return ret

    @classmethod
    def check_paquet(cls, paquet):
        """Vérifie si le paquet spécifié est valide."""
        if paquet not in cls.paquets_:
            raise ValueError(f"Le paquet doit être un des suivants : {cls.paquets_}")

    @classmethod
    def get_forecast(cls, date, paquet="SP1", variables=None, num_workers: int = 4) -> Dict[str, xr.DataArray]:
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
        """Récupère les dernières prévisions disponibles parmi les runs récents.

        Tente de télécharger les données des dernières prévisions en testant successivement les runs les plus récents
        jusqu'à trouver des données valides. Les runs sont testés dans l'ordre chronologique inverse.

        Args:
            paquet (str, optional): Le paquet de données à télécharger. Doit faire partie de cls.paquets_.
                Defaults to "SP1".
            variables (str|List[str], optional): Variable(s) à extraire des fichiers GRIB. Si None, toutes les variables
                sont conservées. Defaults to None.
            num_workers (int, optional): Nombre de workers pour le téléchargement parallèle. Defaults to 4.

        Returns:
            Dict[str, xr.DataArray]: Dictionnaire des DataArrays des variables demandées, avec les coordonnées
                géographiques encodées selon les conventions CF.

        Raises:
            ValueError: Si le paquet spécifié n'est pas valide.
            requests.HTTPError: Si aucun paquet valide n'a été trouvé parmi les cls.past_runs_ derniers runs.
        """
        cls.check_paquet(paquet)
        latest_possible_date = pd.Timestamp.utcnow().floor(f"{cls.freq_update}h")

        for k in range(cls.past_runs_):
            current_date = latest_possible_date - pd.Timedelta(hours=cls.freq_update * k)
            datasets = cls.get_forecast(
                date=current_date,
                paquet=paquet,
                variables=variables,
                num_workers=num_workers,
            )
            if datasets:
                return datasets
        raise requests.HTTPError(f"Aucun paquet n'a été trouvé parmi les {cls.past_runs_} derniers runs.")


def common_process(ds: xr.DataArray) -> xr.DataArray:
    ds["longitude"] = xr.where(
        ds["longitude"] <= 180.0,
        ds["longitude"],
        ds["longitude"] - 360.0,
        keep_attrs=True,
    )
    ds = ds.sortby("longitude").sortby("latitude")
    return ds


class HourlyProcess:
    @staticmethod
    def _process_ds(ds: xr.DataArray) -> xr.DataArray:
        ds = ds.expand_dims("valid_time").drop_vars("time").rename(valid_time="time")
        ds = common_process(ds)
        return ds


class MultiHourProcess:
    @staticmethod
    def _process_ds(ds: xr.DataArray) -> xr.DataArray:
        if "time" in ds.coords:
            ds = ds.drop_vars("time")
        if "step" in ds.dims:
            ds = ds.swap_dims(step="valid_time").rename(valid_time="time")
        ds = common_process(ds)
        return ds
