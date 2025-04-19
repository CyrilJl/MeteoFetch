import os
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from pathlib import Path
from shutil import copyfileobj
from tempfile import TemporaryDirectory
from typing import Dict

import cfgrib
import requests
import xarray as xr

from ._misc import geo_encode_cf


class Model:
    TIMEOUT = 10
    base_url = None
    past_runs_ = 8
    groups_ = ()
    freq_update = None

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @classmethod
    def _url_to_file(cls, url: str, tempdir: TemporaryDirectory) -> Path:
        """Télécharge un fichier depuis une URL et le sauvegarde dans un répertoire temporaire.
        Meilleure gestion de la mémoire pour les fichiers volumineux.
        Utilise une taille de tampon de 16 Mo pour le téléchargement.
        """
        try:
            temp_path = Path(tempdir) / os.path.basename(url).replace(":", "-")

            with requests.get(url, stream=True, timeout=cls.TIMEOUT) as r:
                r.raise_for_status()
                with open(temp_path, "wb") as f:
                    copyfileobj(r.raw, f, length=1024 * 1024 * 64)
            return temp_path
        except Exception:
            return False

    @classmethod
    def _download_urls(cls, urls, path, num_workers):
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            paths = executor.map(lambda url: cls._url_to_file(url, path), urls)
        return list(paths)

    @classmethod
    def _read_grib(cls, path):
        return cfgrib.open_datasets(path, backend_kwargs={"decode_timedelta": True, "indexpath": ""}, cache=False)

    @classmethod
    def _read_multiple_gribs(cls, paths, variables, num_workers) -> Dict[str, xr.DataArray]:
        """Lit les fichiers GRIB en parallèle avec multiprocessing."""
        ret = {}

        with Pool(processes=num_workers) as pool:
            # Traiter les fichiers en parallèle et recevoir les résultats au fur et à mesure
            for datasets in pool.imap(cls._read_grib, paths):
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
