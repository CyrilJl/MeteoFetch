import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from shutil import copyfileobj
from tempfile import TemporaryDirectory
from typing import Dict

import cfgrib
import pandas as pd
import requests
import xarray as xr

from ._misc import geo_encode_cf


class Model:
    """Classe de base pour le téléchargement et le traitement des données de modèles"""

    TIMEOUT = 240
    base_url_ = "https://object.data.gouv.fr/meteofrance-pnt/pnt"
    past_runs_ = 8

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @classmethod
    def check_paquet(cls, paquet):
        """Vérifie si le paquet spécifié est valide."""
        if paquet not in cls.paquets_:
            raise ValueError(f"Le paquet doit être un des suivants : {cls.paquets_}")

    @classmethod
    def _url_to_file(cls, url: str, tempdir: TemporaryDirectory) -> Path:
        """Télécharge un fichier depuis une URL et le sauvegarde dans un répertoire temporaire.
        Meilleure gestion de la mémoire pour les fichiers volumineux.
        Utilise une taille de tampon de 16 Mo pour le téléchargement.
        """
        try:
            temp_path = Path(tempdir) / os.path.basename(url).replace(":", "-")

            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(temp_path, "wb") as f:
                    copyfileobj(r.raw, f, length=1024 * 1024 * 64)
            return temp_path
        except Exception:
            return False

    @classmethod
    def _download_groups(cls, urls, path, num_workers):
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            paths = executor.map(lambda url: cls._url_to_file(url, path), urls)
        return list(paths)

    @classmethod
    def _download_paquet(cls, date, paquet, path, num_workers):
        cls.check_paquet(paquet)

        urls = [cls.base_url_ + "/" + cls.url_.format(date=date, paquet=paquet, group=group) for group in cls.groups_]
        paths = cls._download_groups(urls, path, num_workers)
        if not all(paths):
            return []
        else:
            return paths

    @classmethod
    def _read_paquet(cls, paths, variables):
        ret = {}
        for path in paths:
            datasets = cfgrib.open_datasets(
                path=path, backend_kwargs={"indexpath": "", "decode_timedelta": True}, cache=False
            )
            for ds in datasets:
                for field in ds.data_vars:
                    if variables and field not in variables:
                        continue
                    if field not in ret:
                        ret[field] = []
                    if os.environ.get("meteofetch_test_mode") == "1":
                        ret[field].append(ds[field].isnull(keep_attrs=True))
                    else:
                        ret[field].append(cls._process_ds(ds[field].load()))
        for field in ret:
            ret[field] = xr.concat(ret[field], dim="time", coords="minimal", compat="override")
            ret[field] = geo_encode_cf(ret[field])
        return ret

    @classmethod
    def get_forecast(
        cls,
        date,
        paquet="SP1",
        variables=None,
        path=None,
        return_data=True,
        num_workers: int = 4,
    ) -> Dict[str, xr.DataArray]:
        cls.check_paquet(paquet)
        date_dt = pd.to_datetime(str(date)).floor(f"{cls.freq_update}h")
        date_str = f"{date_dt:%Y-%m-%dT%H}"

        if (path is None) and (not return_data):
            raise ValueError("Le chemin doit être spécifié si return_data est False.")

        with TemporaryDirectory(prefix="meteofetch_") as tempdir:
            if path is None:
                path = tempdir

            paths = cls._download_paquet(
                date=date_str,
                paquet=paquet,
                path=path,
                num_workers=num_workers,
            )
            if return_data:
                return cls._read_paquet(paths, variables)
            else:
                return paths

    @classmethod
    def get_latest_forecast(
        cls,
        paquet="SP1",
        variables=None,
        path=None,
        return_data=True,
        num_workers: int = 4,
    ) -> Dict[str, xr.DataArray]:
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
            ret = cls.get_forecast(
                date=current_date,
                paquet=paquet,
                variables=variables,
                path=path,
                return_data=return_data,
                num_workers=num_workers,
            )
            if ret:
                return ret

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
