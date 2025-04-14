import os
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from pathlib import Path
from shutil import copyfileobj
from tempfile import TemporaryDirectory
from typing import Dict

import cfgrib
import pandas as pd
import requests
import xarray as xr

from ._misc import geo_encode_cf


class Ecmwf:
    """Classe de récupération des données forecast opérationnelles ECMWF
    https://www.ecmwf.int/en/forecasts/datasets/open-data
    """

    TIMEOUT = 60
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
    def _url_to_file(cls, url: str, tempdir: TemporaryDirectory) -> Path:
        """Télécharge un fichier depuis une URL et le sauvegarde dans un répertoire temporaire."""
        try:
            temp_path = Path(tempdir) / os.path.basename(url)

            with requests.get(url, stream=True, timeout=cls.TIMEOUT) as r:
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
    def _download_paquet(cls, date, path, num_workers):
        """Télécharge les fichiers pour un paquet donné."""
        date_dt = pd.to_datetime(date)
        ymd, hour = f"{date_dt:%Y%m%d}", f"{date_dt:%H}"

        urls = [cls.base_url_ + "/" + cls.url_.format(ymd=ymd, hour=hour, group=group) for group in cls.groups_]
        paths = cls._download_groups(urls, path, num_workers)
        if not all(paths):
            return []
        else:
            return paths

    @classmethod
    def _read_path(cls, path):
        return cfgrib.open_datasets(path, backend_kwargs={"decode_timedelta": True, "indexpath": ""}, cache=False)

    @classmethod
    def _read_paquet(cls, paths, variables, num_workers):
        """Lit les fichiers GRIB en parallèle avec multiprocessing."""
        ret = {}

        with Pool(processes=num_workers) as pool:
            # Traiter les fichiers en parallèle et recevoir les résultats au fur et à mesure
            for datasets in pool.imap_unordered(cls._read_path, paths):
                for ds in datasets:
                    for field in ds.data_vars:
                        if variables and field not in variables:
                            continue
                        if field not in ret:
                            ret[field] = []
                        if os.environ.get("meteofetch_test_mode") == "1":
                            ds[field] = ds[field].isnull(keep_attrs=True)
                        ret[field].append(cls._process_ds(ds[field]))

        # Concaténer les résultats pour chaque champ
        for field in ret:
            ret[field] = xr.concat(ret[field], dim="time", coords="minimal", compat="override")
            ret[field] = geo_encode_cf(ret[field])

        return ret

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
                datasets = cls._read_paquet(paths=paths, variables=variables, num_workers=num_workers)
                if path is None:
                    for da in datasets.values():
                        da.load()
                return datasets
            else:
                return paths

    @classmethod
    def get_latest_forecast(
        cls,
        variables=None,
        path=None,
        return_data=True,
        num_workers: int = 4,
    ) -> Dict[str, xr.DataArray]:
        """Récupère les dernières prévisions disponibles parmi les runs récents."""
        latest_possible_date = pd.Timestamp.utcnow().floor(f"{cls.freq_update}h")

        for k in range(cls.past_runs_):
            current_date = latest_possible_date - pd.Timedelta(hours=cls.freq_update * k)
            ret = cls.get_forecast(
                date=current_date,
                variables=variables,
                path=path,
                return_data=return_data,
                num_workers=num_workers,
            )
            if ret:
                return ret

        raise requests.HTTPError(f"Aucun paquet n'a été trouvé parmi les {cls.past_runs_} derniers runs.")
