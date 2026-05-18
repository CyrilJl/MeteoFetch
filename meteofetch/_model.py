import logging
import os
from concurrent.futures import ThreadPoolExecutor
from glob import glob
from multiprocessing import Pool
from os.path import basename, getsize
from pathlib import Path
from platform import system
from shutil import copyfileobj
from subprocess import CalledProcessError, run
from typing import Dict, List, Union

import cfgrib
import requests
import xarray as xr

from ._misc import geo_encode_cf

logger = logging.getLogger(__name__)


class Model:
    TIMEOUT = 10
    base_url = None
    past_runs_ = 8
    groups_ = ()
    freq_update = None

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @staticmethod
    def _process_ds(ds):
        raise NotImplementedError

    @classmethod
    def _url_to_file(cls, url: str, tempdir: str, num_retries: int = 1) -> Union[Path, bool]:
        """Télécharge un fichier depuis une URL et le sauvegarde dans un répertoire temporaire.
        En cas d'échec, la tentative est répétée jusqu'à num_retries fois supplémentaires.
        Utilise une taille de tampon de 64 Mo pour le téléchargement.
        """
        for attempt in range(num_retries + 1):
            try:
                temp_path = Path(tempdir) / os.path.basename(url).replace(":", "-")
                with requests.get(url, stream=True, timeout=cls.TIMEOUT) as r:
                    r.raise_for_status()
                    with open(temp_path, "wb") as f:
                        copyfileobj(r.raw, f, length=1024 * 1024 * 64)
                logger.debug("Downloaded %s", url)
                return temp_path
            except (requests.exceptions.RequestException, OSError) as e:
                if attempt < num_retries:
                    logger.warning("Download attempt %d/%d failed for %s: %s — retrying", attempt + 1, num_retries + 1, url, e)
                else:
                    logger.error("All %d download attempt(s) failed for %s: %s", num_retries + 1, url, e)
        return False

    @classmethod
    def _download_urls(cls, urls, path, num_workers, num_retries: int = 1):
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            paths = executor.map(lambda url: cls._url_to_file(url, path, num_retries), urls)
        return list(paths)

    @classmethod
    def _read_grib(cls, path) -> List[xr.Dataset]:
        """cfgrib ne gère pas les fichiers de plus de 2 Go sur Windows:
        Dans ce cas, on utilise grib_copy pour diviser le fichier en gribs
        contenant chacun une seule variable
        """
        kw = dict(backend_kwargs={"decode_timedelta": True, "indexpath": ""}, cache=False)
        if system() == "Windows" and getsize(path) >= 2**31:
            file_name = basename(path).split(".")[0]
            path_split = Path(path).parent / f"split_{file_name}_[shortName].grib2"
            command = f"grib_copy {path} {path_split.resolve()}"
            try:
                run(command, check=True)
                Path(path).unlink()
                paths = glob(str(Path(path).parent / f"split_{file_name}_*.grib2"))
                datasets = []
                for path_variable in paths:
                    datasets.append(cfgrib.open_dataset(path=path_variable, **kw))
                return datasets
            except CalledProcessError:
                raise
        else:
            # Cas le plus courant
            return cfgrib.open_datasets(path=path, **kw)

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
