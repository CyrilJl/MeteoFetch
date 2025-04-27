from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from typing import Dict

import pandas as pd
import requests
import xarray as xr

from ._misc import is_downloadable
from ._model import Model


class Ecmwf(Model):
    """Classe de récupération des données forecast opérationnelles ECMWF
    https://www.ecmwf.int/en/forecasts/datasets/open-data
    """

    base_url_ = "https://data.ecmwf.int/ecpds/home/opendata"
    past_runs_ = 8
    freq_update = 12
    url_ = "{ymd}/{hour}z/ifs/0p25/oper/{ymd}{hour}0000-{group}h-oper-fc.grib2"
    groups_ = tuple(range(0, 146, 3)) + tuple(range(150, 366, 6))

    @staticmethod
    def _process_ds(ds):
        ds = ds.expand_dims("valid_time").drop_vars("time").rename(valid_time="time")
        ds = ds.sortby("latitude")
        return ds

    @classmethod
    def _get_urls(cls, date) -> list:
        """Génère les URLs pour télécharger les fichiers GRIB2."""
        date_dt = pd.to_datetime(date)
        ymd, hour = f"{date_dt:%Y%m%d}", f"{date_dt:%H}"
        urls = [cls.base_url_ + "/" + cls.url_.format(ymd=ymd, hour=hour, group=group) for group in cls.groups_]
        return urls

    @classmethod
    def _download_paquet(cls, date, path, num_workers):
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
        date,
        variables=None,
        path=None,
        return_data=True,
        num_workers: int = 4,
    ) -> Dict[str, xr.DataArray]:
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
    def get_latest_forecast_time(cls) -> pd.Timestamp:
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
            with ThreadPoolExecutor() as executor:
                downloadables = list(executor.map(is_downloadable, urls))
            if all(downloadables):
                return date
        return False

    @classmethod
    def get_latest_forecast(
        cls,
        variables=None,
        path=None,
        return_data=True,
        num_workers: int = 4,
    ) -> Dict[str, xr.DataArray]:
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
