from tempfile import TemporaryDirectory
from typing import Dict

import pandas as pd
import requests
import xarray as xr

from ._misc import is_downloadable
from ._model import Model


class MeteoFrance(Model):
    """Classe de base pour le téléchargement et le traitement des données de modèles"""

    base_url_ = "https://object.data.gouv.fr/meteofrance-pnt/pnt"
    past_runs_ = 8

    @classmethod
    def _get_groups(cls, paquet):
        """Méthode overwritten par les modèles OutreMer"""
        return cls.groups_

    @classmethod
    def check_paquet(cls, paquet):
        """Vérifie si le paquet spécifié est valide."""
        if paquet not in cls.paquets_:
            raise ValueError(f"Le paquet doit être un des suivants : {cls.paquets_}")

    @classmethod
    def _get_urls(cls, paquet, date) -> list:
        urls = [
            cls.base_url_ + "/" + cls.url_.format(date=date, paquet=paquet, group=group)
            for group in cls._get_groups(paquet=paquet)
        ]
        return urls

    @classmethod
    def _download_paquet(cls, date, paquet, path, num_workers):
        cls.check_paquet(paquet)

        urls = cls._get_urls(paquet=paquet, date=date)
        paths = cls._download_urls(urls, path, num_workers)
        if not all(paths):
            return []
        else:
            return paths

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
                datasets = cls._read_multiple_gribs(paths=paths, variables=variables, num_workers=num_workers)
                if path is None:
                    for da in datasets:
                        da.load()
                return datasets
            else:
                return paths

    @classmethod
    def get_latest_forecast_time(cls, paquet):
        latest_possible_date = pd.Timestamp.utcnow().floor(f"{cls.freq_update}h")
        for k in range(cls.past_runs_):
            date = latest_possible_date - pd.Timedelta(hours=cls.freq_update * k)
            urls = cls._get_urls(paquet=paquet, date=f"{date:%Y-%m-%dT%H}")
            downloadable = all([is_downloadable(url) for url in urls])
            if downloadable:
                return date
        return False

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
        date = cls.get_latest_forecast_time(paquet=paquet)
        if date:
            ret = cls.get_forecast(
                date=date,
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
    ds.attrs["Packaged by"] = "meteofetch"
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
