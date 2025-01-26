from collections import defaultdict
from tempfile import NamedTemporaryFile
from typing import Dict, List

import cfgrib
import pandas as pd
import requests
import xarray as xr


class Arome:
    @classmethod
    def _download_file(cls, url: str) -> List[xr.Dataset]:
        with requests.get(url=url) as response:
            response.raise_for_status()
            with NamedTemporaryFile(delete=False, suffix=".grib2") as tmp_file:
                tmp_file.write(response.content)
                datasets = cfgrib.open_datasets(tmp_file.name, indexpath="")
                for k in range(len(datasets)):
                    datasets[k] = cls._process_ds(datasets[k]).load()
        return datasets

    @classmethod
    def _download_paquet(cls, date, paquet) -> Dict[str, xr.DataArray]:
        datasets = defaultdict(list)
        for group in cls.groups_:
            url = cls.url_.format(date=date, paquet=paquet, group=group)
            datasets_group = cls._download_file(url)
            for ds in datasets_group:
                for field in ds.data_vars:
                    if field != "unknown":
                        datasets[field].append(ds[field])
        for field in datasets:
            datasets[field] = xr.concat(datasets[field], dim="time").squeeze()
        return datasets

    @classmethod
    def check_paquet(cls, paquet):
        if paquet not in cls.paquets_:
            raise ValueError(f"paquet must be one of {cls.paquets_}")

    @classmethod
    def get_forecast(cls, date, paquet="SP1") -> Dict[str, xr.DataArray]:
        cls.check_paquet(paquet)
        date = pd.to_datetime(str(date)).floor("3h")
        return cls._download_paquet(date=f"{date:%Y-%m-%dT%H}", paquet=paquet)

    @classmethod
    def get_latest_forecast(cls, paquet="SP1") -> Dict[str, xr.DataArray]:
        """Get the latest forecast available for a given paquet. Each paquet
        contains different fields.
        Returns:
            Dict[str, xr.DataArray]: A dictionary containing the forecast fields.
        """
        cls.check_paquet(paquet)
        date = pd.Timestamp.utcnow().floor("3h")
        for k in range(8):
            try:
                return cls.get_forecast(date=date-pd.Timedelta(hours=3*k), paquet=paquet)
            except requests.HTTPError:
                continue
        raise requests.HTTPError("No forecast found")


class Arome001(Arome):
    """
    Regroupement de différents paramètres du modèle atmosphérique français à aire limitée et à haute résolution AROME, en fichiers horaires.

    Données d’analyse et de prévision en points de grille régulière.

    Grille EURW1S100 (55,4N 37,5N 12W 16E) - Pas de temps : 1h"""

    groups_ = tuple([f"{h:02d}H" for h in range(52)])
    paquets_ = ("SP1", "SP2", "SP3", "HP1")
    url_ = "https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arome/001/{paquet}/arome__001__{paquet}__{group}__{date}:00:00Z.grib2"

    @staticmethod
    def _process_ds(ds) -> xr.Dataset:
        ds = ds.expand_dims("valid_time").drop_vars("time").rename(valid_time="time")
        return ds


class Arome0025(Arome):
    """
    Regroupement de différents paramètres du modèle atmosphérique français à aire limitée et à haute résolution AROME, répartis en plusieurs groupes d’échéances : 00h-06h, 07h-12h, 13h-18h, 19h-24h, 25h-30h, 31h-36h, 37h-42h, 43h-48h et 49h-51h.

    Données d’analyse et de prévision en points de grille régulière.

    Grille EURW1S40 (55,4N 37,5N 12W 16E) - Pas de temps : 1h
    """

    groups_ = ("00H06H", "07H12H", "13H18H", "19H24H", "25H30H", "31H36H", "37H42H", "43H48H", "49H51H")
    paquets_ = ("SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3")
    url_ = "https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arome/0025/{paquet}/arome__0025__{paquet}__{group}__{date}:00:00Z.grib2"

    @staticmethod
    def _process_ds(ds) -> xr.Dataset:
        if "time" in ds:
            ds = ds.drop_vars("time")
        if "step" in ds.dims:
            ds = ds.swap_dims(step="valid_time").rename(valid_time="time")
        return ds
