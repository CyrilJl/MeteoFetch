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
import pandas as pd
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

    @classmethod
    def _iter_run_dates(cls) -> List[pd.Timestamp]:
        """Return candidate run timestamps in reverse-chronological order (UTC).

        Starts from the most recent floored run time and steps back by
        ``freq_update`` hours, up to ``past_runs_`` entries.
        """
        freq = cls.freq_update
        assert freq is not None, "freq_update must be set on concrete model subclasses"
        latest = pd.Timestamp.utcnow().floor(f"{freq}h")
        return [latest - pd.Timedelta(hours=freq * k) for k in range(cls.past_runs_)]

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
    def _download_urls(cls, urls: List[str], path: str, num_workers: int, num_retries: int = 1) -> List[Union[Path, bool]]:
        """Download a list of URLs in parallel and return their local paths.

        Args:
            urls: Remote URLs to download.
            path: Directory where files are saved.
            num_workers: Number of parallel download threads.
            num_retries: Number of additional attempts per file on failure.

        Returns:
            List of ``Path`` objects for successful downloads, ``False`` for failures.
        """
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            paths = executor.map(lambda url: cls._url_to_file(url, path, num_retries), urls)
        return list(paths)

    @classmethod
    def _read_grib(cls, path) -> List[xr.Dataset]:
        """Open a GRIB2 file and return a list of datasets (one per variable group).

        On Windows, cfgrib cannot handle files larger than 2 GB. In that case the
        file is first split into per-variable files using ``grib_copy``, then each
        split file is opened individually.
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
        """Read GRIB files in parallel and merge results by field name.

        Args:
            paths: Local GRIB file paths to read.
            variables: If non-empty, only these field names are kept.
            num_workers: Number of worker processes for parallel reading.

        Returns:
            Dict mapping field name → concatenated ``xr.DataArray`` (CF-encoded).

        Note:
            When test mode is active (see ``set_test_mode()``), field values are
            replaced with their ``isnull()`` boolean mask to avoid loading real data.
        """
        ret: Dict[str, list] = {}

        with Pool(processes=num_workers) as pool:
            for datasets in pool.imap(cls._read_grib, paths):
                for ds in datasets:
                    for _field in ds.data_vars:
                        field = str(_field)
                        if variables and field not in variables:
                            continue
                        if field not in ret:
                            ret[field] = []
                        if os.environ.get("METEOFETCH_TEST_MODE") == "1":  # set via set_test_mode()
                            ds[field] = ds[field].isnull(keep_attrs=True)
                        ret[field].append(cls._process_ds(ds[field]))

        result: Dict[str, xr.DataArray] = {}
        for field in ret:
            result[field] = xr.concat(ret[field], dim="time", coords="minimal", compat="override")
            result[field] = geo_encode_cf(result[field])

        return result
