import logging
from tempfile import TemporaryDirectory
from typing import Dict, Optional, Union

import pandas as pd
import requests
import xarray as xr

from .._misc import are_downloadable
from .._model import Model

logger = logging.getLogger(__name__)


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
    def _get_urls(cls, date: Union[str, pd.Timestamp]) -> list:
        """Génère les URLs pour télécharger les fichiers GRIB2."""
        date_dt = pd.to_datetime(date)
        ymd, hour = f"{date_dt:%Y%m%d}", f"{date_dt:%H}"
        urls = [cls.base_url_ + "/" + cls.url_.format(ymd=ymd, hour=hour, group=group) for group in cls.groups_]
        return urls

    @classmethod
    def _download_paquet(cls, date: str, path: str, num_workers: int, num_retries: int = 1) -> list:
        """Télécharge les fichiers pour un paquet donné."""
        urls = cls._get_urls(date=date)
        paths = cls._download_urls(urls, path, num_workers, num_retries)
        if not all(paths):
            logger.error("Some files could not be downloaded for %s run %s", cls.__name__, date)
            return []
        return paths

    @classmethod
    def get_forecast(
        cls,
        date: Union[str, pd.Timestamp],
        variables: Optional[list] = None,
        path: Optional[str] = None,
        return_data: bool = True,
        num_workers: int = 4,
        num_retries: int = 1,
    ) -> Union[Dict[str, xr.DataArray], list]:
        """Récupère les prévisions pour une date donnée.

        Args:
            date (str | pd.Timestamp): Date du run de prévision.
            variables (list, optional): Variables à extraire. Si None, toutes les variables sont conservées.
            path (str, optional): Dossier de destination des fichiers GRIB. Si None, un dossier temporaire est utilisé.
            return_data (bool): Si True, retourne les données en mémoire. Defaults to True.
            num_workers (int): Nombre de workers pour le téléchargement parallèle. Defaults to 4.
            num_retries (int): Nombre de tentatives supplémentaires par fichier en cas d'échec. Defaults to 1.

        Returns:
            Dict[str, xr.DataArray] | list: Données par variable, ou liste de chemins si return_data est False.
        """
        date_dt = pd.to_datetime(str(date)).floor(f"{cls.freq_update}h")
        date_str = f"{date_dt:%Y-%m-%dT%H}"

        if (path is None) and (not return_data):
            raise ValueError("Le chemin doit être spécifié si return_data est False.")

        logger.info("Fetching %s forecast for run %s", cls.__name__, date_str)
        with TemporaryDirectory(prefix="meteofetch_") as tempdir:
            if path is None:
                path = tempdir

            paths = cls._download_paquet(
                date=date_str,
                path=path,
                num_workers=num_workers,
                num_retries=num_retries,
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
    def get_latest_forecast_time(cls) -> Optional[pd.Timestamp]:
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
                logger.info("Latest available %s run: %s", cls.__name__, date)
                return date
        return None

    @classmethod
    def get_latest_forecast(
        cls,
        variables: Optional[list] = None,
        path: Optional[str] = None,
        return_data: bool = True,
        num_workers: int = 4,
        num_retries: int = 1,
    ) -> Union[Dict[str, xr.DataArray], list]:
        """Récupère les dernières prévisions disponibles parmi les runs récents.

        Parcourt les cls.past_runs_ derniers runs dans l'ordre chronologique inverse
        et télécharge le premier run dont toutes les URLs sont accessibles.

        Args:
            variables (list, optional): Variables à extraire. Si None, toutes les variables sont conservées.
            path (str, optional): Dossier de destination des fichiers GRIB. Si None, un dossier temporaire est utilisé.
            return_data (bool): Si True, retourne les données en mémoire. Defaults to True.
            num_workers (int): Nombre de workers pour le téléchargement parallèle. Defaults to 4.
            num_retries (int): Nombre de tentatives supplémentaires par fichier en cas d'échec. Defaults to 1.

        Returns:
            Dict[str, xr.DataArray] | list: Données par variable, ou liste de chemins si return_data est False.

        Raises:
            requests.HTTPError: Si aucun run valide n'a été trouvé parmi les cls.past_runs_ derniers runs.
        """
        date = cls.get_latest_forecast_time()
        if date:
            ret = cls.get_forecast(
                date=date,
                variables=variables,
                path=path,
                return_data=return_data,
                num_workers=num_workers,
                num_retries=num_retries,
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
            urls = cls._get_urls(date=date)
            downloadable = are_downloadable(urls, return_date=return_date)
            ret.append(downloadable)
        return pd.Series(ret, index=index, name=f"{cls.__name__.lower()}")
