from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    past_runs_ = 8

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @classmethod
    def _download_file(cls, url: str, variables: List[str]) -> List[xr.DataArray]:
        try:
            with requests.get(url=url, timeout=cls.TIMEOUT) as response:
                response.raise_for_status()
                with TemporaryDirectory(prefix="meteofetch_") as tmp_dir:
                    file_path = Path(tmp_dir) / "data.grib2"
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    datasets = cfgrib.open_datasets(
                        path=file_path,
                        indexpath="",
                        decode_timedelta=True,
                    )
                    if variables is not None:
                        for ds in datasets:
                            ds = ds.drop_vars([var for var in ds.data_vars if var not in variables])
                    ret = []
                    for _ in range(len(datasets)):
                        ds = datasets.pop()
                        for var in ds.data_vars:
                            ret.append(ds[var].compute())
                    return ret

        except Exception as e:
            raise requests.HTTPError(f"Erreur lors du téléchargement du fichier : {e}")

    @classmethod
    def _download_paquet(cls, date, paquet, variables, num_workers: int) -> Dict[str, xr.DataArray]:
        if isinstance(variables, str):
            variables_ = (variables,)
        else:
            variables_ = variables

        urls_to_download = [
            cls.base_url_ + "/" + cls.url_.format(date=date, paquet=paquet, group=group) for group in cls.groups_
        ]

        ret = defaultdict(list)

        with ThreadPoolExecutor(max_workers=num_workers) as executor:

            def download_task(url):
                return cls._download_file(url, variables_)

            results_iterator = executor.map(download_task, urls_to_download)
            for data_arrays_for_url in results_iterator:
                for da in data_arrays_for_url:
                    ret[da.name].append(da)

        for key in ret.keys():
            ret[key] = xr.concat(ret[key], dim="time")
            ret[key] = cls._process_ds(ret[key])
            ret[key] = geo_encode_cf(ret[key])
            ret[key].attrs["Packaged by"] = "meteofetch"

        return ret

    @classmethod
    def check_paquet(cls, paquet):
        """Vérifie si le paquet spécifié est valide."""
        if paquet not in cls.paquets_:
            raise ValueError(f"paquet must be one of {cls.paquets_}")

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
        cls.check_paquet(paquet)
        latest_possible_date = pd.Timestamp.utcnow().floor(f"{cls.freq_update}h")

        for k in range(cls.past_runs_):
            current_date = latest_possible_date - pd.Timedelta(hours=cls.freq_update * k)
            try:
                return cls.get_forecast(
                    date=current_date,
                    paquet=paquet,
                    variables=variables,
                    num_workers=num_workers,
                )
            except Exception as _:
                pass
        raise requests.HTTPError(f"Aucun paquet n'a été trouvé parmi les derniers {cls.past_runs_} runs.")


def common_process(ds: xr.Dataset) -> xr.Dataset:
    ds["longitude"] = xr.where(
        ds["longitude"] <= 180.0,
        ds["longitude"],
        ds["longitude"] - 360.0,
        keep_attrs=True,
    )
    ds = ds.sortby("longitude").sortby("latitude")

    if "time" in ds.dims:
        ds = ds.sortby("time")
    return ds


class HourlyProcess:
    @staticmethod
    def _process_ds(ds) -> xr.Dataset:
        ds = ds.expand_dims("valid_time").drop_vars("time").rename(valid_time="time")
        ds = common_process(ds)
        return ds


class MultiHourProcess:
    @staticmethod
    def _process_ds(ds) -> xr.Dataset:
        if "time" in ds:
            ds = ds.drop_vars("time")
        if "step" in ds.dims:
            ds = ds.swap_dims(step="valid_time").rename(valid_time="time")
        ds = common_process(ds)
        return ds
