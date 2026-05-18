import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List, Literal, Optional, Union, overload

import pandas as pd
import xarray as xr

from .._misc import ForecastNotAvailableError, are_downloadable
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
    def _get_urls(cls, date: Union[str, pd.Timestamp]) -> List[str]:
        """Build the list of GRIB2 download URLs for a given run date."""
        date_dt = pd.to_datetime(date)
        ymd, hour = f"{date_dt:%Y%m%d}", f"{date_dt:%H}"
        return [cls.base_url_ + "/" + cls.url_.format(ymd=ymd, hour=hour, group=group) for group in cls.groups_]

    @classmethod
    def _download_paquet(cls, date: str, path: str, num_workers: int, num_retries: int = 1) -> List[Path]:
        """Download all GRIB files for a run date into *path*.

        Returns an empty list if any file fails to download.
        """
        urls = cls._get_urls(date=date)
        paths = cls._download_urls(urls, path, num_workers, num_retries)
        if not all(paths):
            logger.error("Some files could not be downloaded for %s run %s", cls.__name__, date)
            return []
        return [p for p in paths if isinstance(p, Path)]

    @classmethod
    @overload
    def get_forecast(
        cls,
        date: Union[str, pd.Timestamp],
        variables: Optional[list] = ...,
        path: Optional[str] = ...,
        return_data: Literal[True] = ...,
        num_workers: int = ...,
        num_retries: int = ...,
    ) -> Dict[str, xr.DataArray]: ...

    @classmethod
    @overload
    def get_forecast(
        cls,
        date: Union[str, pd.Timestamp],
        variables: Optional[list] = ...,
        path: Optional[str] = ...,
        return_data: Literal[False] = ...,
        num_workers: int = ...,
        num_retries: int = ...,
    ) -> List[Path]: ...

    @classmethod
    def get_forecast(
        cls,
        date: Union[str, pd.Timestamp],
        variables: Optional[list] = None,
        path: Optional[str] = None,
        return_data: bool = True,
        num_workers: int = 4,
        num_retries: int = 1,
    ) -> Union[Dict[str, xr.DataArray], List[Path]]:
        """Fetch the forecast for a given run date.

        Args:
            date: Run date/time. Floored to the nearest ``freq_update`` hour boundary.
            variables: Field names to keep. If ``None``, all fields are returned.
            path: Directory for GRIB files. Uses a temporary directory if ``None``.
            return_data: If ``True``, load data into memory and return a dict of
                DataArrays. If ``False``, save files to *path* and return their paths.
            num_workers: Parallel download/read workers.
            num_retries: Extra download attempts per file on failure.

        Returns:
            Dict of ``xr.DataArray`` (CF-encoded) when ``return_data=True``,
            or list of ``Path`` objects when ``return_data=False``.

        Raises:
            ValueError: If ``path`` is ``None`` and ``return_data`` is ``False``.
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
        """Return the most recent run timestamp for which all files are available.

        Iterates over the last ``past_runs_`` run times in reverse-chronological
        order (UTC) and returns the first one whose URLs are all reachable.

        Returns:
            The latest available run ``pd.Timestamp``, or ``None`` if none found.
        """
        for date in cls._iter_run_dates():
            if are_downloadable(cls._get_urls(date=date)):
                logger.info("Latest available %s run: %s", cls.__name__, date)
                return date
        return None

    @classmethod
    @overload
    def get_latest_forecast(
        cls,
        variables: Optional[list] = ...,
        path: Optional[str] = ...,
        return_data: Literal[True] = ...,
        num_workers: int = ...,
        num_retries: int = ...,
    ) -> Dict[str, xr.DataArray]: ...

    @classmethod
    @overload
    def get_latest_forecast(
        cls,
        variables: Optional[list] = ...,
        path: Optional[str] = ...,
        return_data: Literal[False] = ...,
        num_workers: int = ...,
        num_retries: int = ...,
    ) -> List[Path]: ...

    @classmethod
    def get_latest_forecast(
        cls,
        variables: Optional[list] = None,
        path: Optional[str] = None,
        return_data: bool = True,
        num_workers: int = 4,
        num_retries: int = 1,
    ) -> Union[Dict[str, xr.DataArray], List[Path]]:
        """Fetch the most recent available forecast.

        Iterates over the last ``past_runs_`` run times (newest first) and
        downloads the first run whose files are all reachable.

        Args:
            variables: Field names to keep. If ``None``, all fields are returned.
            path: Directory for GRIB files. Uses a temporary directory if ``None``.
            return_data: If ``True``, return a dict of DataArrays. If ``False``,
                save files to *path* and return their paths.
            num_workers: Parallel download/read workers.
            num_retries: Extra download attempts per file on failure.

        Returns:
            Dict of ``xr.DataArray`` (CF-encoded) when ``return_data=True``,
            or list of ``Path`` objects when ``return_data=False``.

        Raises:
            ForecastNotAvailableError: If no valid run is found among the last
                ``past_runs_`` runs.
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
        raise ForecastNotAvailableError(
            f"No valid {cls.__name__} run found among the last {cls.past_runs_} runs."
        )

    @classmethod
    def availability(cls, return_date: bool = False) -> pd.Series:
        """Check download availability for the last ``past_runs_`` run times.

        Args:
            return_date: If ``True``, return the ``Last-Modified`` date for each
                run instead of a boolean.

        Returns:
            ``pd.Series`` indexed by run timestamp.
        """
        index, ret = [], []
        for date in cls._iter_run_dates():
            index.append(date)
            ret.append(are_downloadable(cls._get_urls(date=date), return_date=return_date))
        return pd.Series(ret, index=index, name=f"{cls.__name__.lower()}")
