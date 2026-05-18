import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List, Literal, Optional, Union, overload

import pandas as pd
import xarray as xr

from .._misc import ForecastNotAvailableError, are_downloadable
from .._model import Model

logger = logging.getLogger(__name__)

# All paquet identifiers used across MeteoFrance models.
Paquet = Literal["SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3"]


class MeteoFrance(Model):
    """Base class for all Meteo-France models."""

    base_url_: str = "https://meteofrance-pnt.s3.rbx.io.cloud.ovh.net/pnt"
    past_runs_: int = 8
    paquets_: tuple
    url_: str
    freq_update: int

    @classmethod
    def _get_groups(cls, paquet: Paquet) -> tuple:
        """Return the group identifiers for *paquet* (overridden by OutreMer models)."""
        return cls.groups_

    @classmethod
    def check_paquet(cls, paquet: Paquet) -> None:
        """Raise ``ValueError`` if *paquet* is not valid for this model."""
        if paquet not in cls.paquets_:
            raise ValueError(f"paquet must be one of {cls.paquets_}, got {paquet!r}")

    @classmethod
    def _get_urls(cls, paquet: Paquet, date: str) -> List[str]:
        """Build the list of GRIB2 download URLs for a given paquet and run date."""
        return [
            cls.base_url_ + "/" + cls.url_.format(date=date, paquet=paquet, group=group)
            for group in cls._get_groups(paquet=paquet)
        ]

    @classmethod
    def _download_paquet(
        cls, date: str, paquet: Paquet, path: str, num_workers: int, num_retries: int = 1
    ) -> List[Path]:
        """Download all GRIB files for a paquet/run-date into *path*.

        Returns an empty list if any file fails to download.
        """
        cls.check_paquet(paquet)
        urls = cls._get_urls(paquet=paquet, date=date)
        paths = cls._download_urls(urls, path, num_workers, num_retries)
        if not all(paths):
            logger.error("Some files could not be downloaded for %s paquet=%s run %s", cls.__name__, paquet, date)
            return []
        return [p for p in paths if isinstance(p, Path)]

    @classmethod
    @overload
    def get_forecast(
        cls,
        date: Union[str, pd.Timestamp],
        paquet: Paquet = ...,
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
        paquet: Paquet = ...,
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
        paquet: Paquet = "SP1",
        variables: Optional[list] = None,
        path: Optional[str] = None,
        return_data: bool = True,
        num_workers: int = 4,
        num_retries: int = 1,
    ) -> Union[Dict[str, xr.DataArray], List[Path]]:
        """Fetch the forecast for a given run date and paquet.

        Args:
            date: Run date/time. Floored to the nearest ``freq_update`` hour boundary.
            paquet: Data package identifier. Must be in ``cls.paquets_``. Defaults to ``"SP1"``.
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
            ValueError: If *paquet* is invalid, or if *path* is ``None`` and
                ``return_data`` is ``False``.
        """
        cls.check_paquet(paquet)
        date_dt = pd.to_datetime(str(date)).floor(f"{cls.freq_update}h")
        date_str = f"{date_dt:%Y-%m-%dT%H}"

        if (path is None) and (not return_data):
            raise ValueError("Le chemin doit être spécifié si return_data est False.")

        logger.info("Fetching %s forecast for run %s (paquet=%s)", cls.__name__, date_str, paquet)
        with TemporaryDirectory(prefix="meteofetch_") as tempdir:
            if path is None:
                path = tempdir

            paths = cls._download_paquet(
                date=date_str,
                paquet=paquet,
                path=path,
                num_workers=num_workers,
                num_retries=num_retries,
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
    def availability_paquet(cls, paquet: Paquet, return_date: bool = False) -> pd.Series:
        """Check download availability for a single paquet across recent run times.

        Args:
            paquet: Package identifier to check.
            return_date: If ``True``, return the ``Last-Modified`` date for each
                run instead of a boolean.

        Returns:
            ``pd.Series`` indexed by run timestamp, named after *paquet*.
        """
        index, ret = [], []
        for date in cls._iter_run_dates():
            index.append(date)
            ret.append(are_downloadable(cls._get_urls(paquet=paquet, date=f"{date:%Y-%m-%dT%H}"), return_date=return_date))
        return pd.Series(ret, index=index, name=paquet)

    @classmethod
    def availability(cls, return_date: bool = False) -> pd.DataFrame:
        """Check availability for all paquets across the last ``past_runs_`` runs.

        Args:
            return_date: If ``True``, return ``Last-Modified`` dates instead of booleans.

        Returns:
            ``pd.DataFrame`` with paquets as columns and run timestamps as the index.
        """
        with ThreadPoolExecutor() as executor:
            ret = list(
                executor.map(
                    lambda paquet: cls.availability_paquet(paquet=paquet, return_date=return_date),
                    cls.paquets_,
                )
            )
        return pd.concat(ret, axis=1)

    @classmethod
    def get_latest_forecast_time(cls, paquet: Paquet) -> Optional[pd.Timestamp]:
        """Return the most recent run timestamp for which all paquet files are available.

        Args:
            paquet: Package identifier to check.

        Returns:
            The latest available run ``pd.Timestamp``, or ``None`` if none found.
        """
        for date in cls._iter_run_dates():
            if are_downloadable(cls._get_urls(paquet=paquet, date=f"{date:%Y-%m-%dT%H}")):
                logger.info("Latest available %s run: %s (paquet=%s)", cls.__name__, date, paquet)
                return date
        return None

    @classmethod
    @overload
    def get_latest_forecast(
        cls,
        paquet: Paquet = ...,
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
        paquet: Paquet = ...,
        variables: Optional[list] = ...,
        path: Optional[str] = ...,
        return_data: Literal[False] = ...,
        num_workers: int = ...,
        num_retries: int = ...,
    ) -> List[Path]: ...

    @classmethod
    def get_latest_forecast(
        cls,
        paquet: Paquet = "SP1",
        variables: Optional[list] = None,
        path: Optional[str] = None,
        return_data: bool = True,
        num_workers: int = 4,
        num_retries: int = 1,
    ) -> Union[Dict[str, xr.DataArray], List[Path]]:
        """Fetch the most recent available forecast for a given paquet.

        Iterates over the last ``past_runs_`` run times (newest first) and
        downloads the first run whose files are all reachable.

        Args:
            paquet: Data package identifier. Must be in ``cls.paquets_``. Defaults to ``"SP1"``.
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
            ValueError: If *paquet* is not valid for this model.
            ForecastNotAvailableError: If no valid run is found among the last
                ``past_runs_`` runs.
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
                num_retries=num_retries,
            )
            if ret:
                return ret
        raise ForecastNotAvailableError(
            f"No valid {cls.__name__} run found for paquet={paquet!r} among the last {cls.past_runs_} runs."
        )


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
