from tempfile import TemporaryDirectory
from typing import Dict

import pandas as pd
import requests
import xarray as xr

from .._misc import are_downloadable
from .._model import Model


class ECMWF(Model):
    """Base class for all ECMWF models."""

    base_url_: str
    past_runs_: int
    freq_update: int
    url_: str
    groups_: tuple

    @staticmethod
    def _process_ds(ds: xr.Dataset) -> xr.Dataset:
        ds = ds.expand_dims("valid_time").drop_vars("time").rename(valid_time="time")
        ds = ds.sortby("latitude")
        return ds

    @classmethod
    def _get_urls(cls, date: pd.Timestamp) -> list:
        """Génère les URLs pour télécharger les fichiers GRIB2."""
        date_dt = pd.to_datetime(date)
        ymd, hour = f"{date_dt:%Y%m%d}", f"{date_dt:%H}"
        urls = [cls.base_url_ + "/" + cls.url_.format(ymd=ymd, hour=hour, group=group) for group in cls.groups_]
        return urls

    @classmethod
    def _download_paquet(cls, date: str, path: str, num_workers: int) -> list:
        """Télécharge les fichiers pour un paquet donné."""
        urls = cls._get_urls(date=date)
        paths = cls._download_urls(urls, path, num_workers)
        if not all(paths):
            return []
        else:
            return paths

    @classmethod
    def get_forecast(
        cls,
        date: str,
        variables: list = None,
        path: str = None,
        return_data: bool = True,
        num_workers: int = 4,
    ) -> Dict[str, xr.DataArray] | list:
        """Récupère les prévisions pour une date donnée."""
        date_dt = pd.to_datetime(str(date)).floor(f"{cls.freq_update}h")
        date_str = f"{date_dt:%Y-%m-%dT%H}"

        if (path is None) and (not return_data):
            raise ValueError("Le chemin doit être spécifié si return_data est False.")

        with TemporaryDirectory(prefix="meteofetch_") as tempdir:
            if path is None:
                path = tempdir

            paths = cls._download_paquet(
                date=date_str,
                path=path,
                num_workers=num_workers,
            )
            if return_data:
                datasets = cls._read_multiple_gribs(paths=paths, variables=variables, num_workers=num_workers)
                if path is None:
                    for da in datasets.values():
                        da.load()
                return datasets
            else:
                return paths

    @classmethod
    def get_latest_forecast_time(cls) -> pd.Timestamp | bool:
        """Trouve l'heure de prévision la plus récente disponible parmi les runs récents.

        Parcourt les cls.past_runs_ derniers runs dans l'ordre chronologique inverse
        et retourne le premier run dont toutes les URLs sont accessibles.

        Returns:
            pd.Timestamp or False: Timestamp du run valide le plus récent, ou False si aucun run valide n'a été trouvé.
        """
        latest_possible_date = pd.Timestamp.now().floor(f"{cls.freq_update}h")
        for k in range(cls.past_runs_):
            date = latest_possible_date - pd.Timedelta(hours=cls.freq_update * k)
            urls = cls._get_urls(date=date)
            if are_downloadable(urls):
                return date
        return False

    @classmethod
    def get_latest_forecast(
        cls,
        variables: list = None,
        path: str = None,
        return_data: bool = True,
        num_workers: int = 4,
    ) -> Dict[str, xr.DataArray] | list:
        """Récupère les dernières prévisions disponibles parmi les runs récents."""
        date = cls.get_latest_forecast_time()
        if date:
            ret = cls.get_forecast(
                date=date,
                variables=variables,
                path=path,
                return_data=return_data,
                num_workers=num_workers,
            )
            if ret:
                return ret
        raise requests.HTTPError(f"Aucun paquet n'a été trouvé parmi les {cls.past_runs_} derniers runs.")

    @classmethod
    def availability(cls, return_date=False):
        latest_possible_date = pd.Timestamp.now().floor(f"{cls.freq_update}h")
        index, ret = [], []
        for k in range(cls.past_runs_):
            date = latest_possible_date - pd.Timedelta(hours=cls.freq_update * k)
            index.append(date)
            urls = cls._get_urls(date=f"{date:%Y-%m-%dT%H}")
            downloadable = are_downloadable(urls, return_date=return_date)
            ret.append(downloadable)
        return pd.Series(ret, index=index, name=f"{cls.__name__.lower()}")
