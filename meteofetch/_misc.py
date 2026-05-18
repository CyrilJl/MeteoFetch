"""
The Well Known Text of WGS 84 is hardcoded in the code to avoid having to import pyproj.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Union

import eccodes
import requests
import xarray as xr

logger = logging.getLogger(__name__)


class ForecastNotAvailableError(RuntimeError):
    """Raised when no valid forecast run is found among the recent past runs."""


CRS_WKT = """
            GEOGCRS[
                "WGS 84",
                ENSEMBLE[
                    "World Geodetic System 1984 ensemble",
                    MEMBER["World Geodetic System 1984 (Transit)"],
                    MEMBER["World Geodetic System 1984 (G730)"],
                    MEMBER["World Geodetic System 1984 (G873)"],
                    MEMBER["World Geodetic System 1984 (G1150)"],
                    MEMBER["World Geodetic System 1984 (G1674)"],
                    MEMBER["World Geodetic System 1984 (G1762)"],
                    MEMBER["World Geodetic System 1984 (G2139)"],
                    MEMBER["World Geodetic System 1984 (G2296)"],
                    ELLIPSOID["WGS 84", 6378137, 298.257223563, LENGTHUNIT["metre", 1]],
                    ENSEMBLEACCURACY[2.0],
                ],
                PRIMEM["Greenwich", 0, ANGLEUNIT["degree", 0.0174532925199433]],
                CS[ellipsoidal, 2],
                AXIS[
                    "geodetic latitude (Lat)",
                    north,
                    ORDER[1],
                    ANGLEUNIT["degree", 0.0174532925199433],
                ],
                AXIS[
                    "geodetic longitude (Lon)",
                    east,
                    ORDER[2],
                    ANGLEUNIT["degree", 0.0174532925199433],
                ],
                USAGE[
                    SCOPE["Horizontal component of 3D system."],
                    AREA["World."],
                    BBOX[-90, -180, 90, 180],
                ],
                ID["EPSG", 4326],
            ]
          """


def geo_encode_cf(da: xr.DataArray) -> xr.DataArray:
    """
    Rend une DataArray conforme aux conventions CF (Climate and Forecast).

    Cette fonction ajoute les attributs et encodages nécessaires pour que la DataArray
    soit compatible avec les outils respectant les conventions CF. Elle inclut la compression,
    les informations de référence spatiale, et les coordonnées géographiques.

    Args:
        da (xr.DataArray): La DataArray à modifier pour la rendre conforme aux conventions CF.

    Returns:
        xr.DataArray: La DataArray modifiée avec les attributs et encodages CF ajoutés.
    """
    da.encoding.update(
        {
            "zlib": True,
            "complevel": 6,
            "grid_mapping": "spatial_ref",
            "coordinates": "latitude longitude",
        }
    )
    da.coords["spatial_ref"] = xr.Variable((), 0)
    da["spatial_ref"].attrs["crs_wkt"] = CRS_WKT
    da["spatial_ref"].attrs["spatial_ref"] = CRS_WKT
    da["spatial_ref"].attrs["grid_mapping_name"] = "latitude_longitude"
    if "time" in da:
        da["time"].encoding = {"units": "hours since 1970-01-01 00:00:00"}
    return da


def set_grib_defs(source: Literal["eccodes", "meteofrance"]) -> None:
    """Switch the GRIB definition source used by eccodes.

    Args:
        source: "eccodes" to use the bundled eccodes definitions (default upstream behaviour),
                or "meteofrance" to use the Météo-France-specific definitions shipped with
                this package (required for some MeteoFrance model fields).
    """
    current_path = os.environ.get("ECCODES_DEFINITION_PATH")

    if source == "eccodes":
        required_path = None
    elif source == "meteofrance":
        required_path = str(Path(__file__).parent / "gribdefs")
    else:
        raise ValueError(f"Source inconnue : {source}")

    if current_path != required_path:
        if source == "eccodes":
            os.environ.pop("ECCODES_DEFINITION_PATH", None)
        else:
            assert isinstance(required_path, str)
            os.environ["ECCODES_DEFINITION_PATH"] = required_path
        print(f"Définitions GRIB mises à jour : {source}")
        eccodes.codes_context_delete()


def set_test_mode() -> None:
    """Enable test mode: replace all downloaded data with boolean (isnull) arrays.

    Sets the ``METEOFETCH_TEST_MODE`` environment variable to ``"1"``.
    When active, ``Model._read_multiple_gribs`` converts every field to a boolean
    mask via ``isnull()``, which lets tests assert on shape and structure without
    downloading or storing real meteorological data.
    """
    os.environ["METEOFETCH_TEST_MODE"] = "1"
    print("Test mode enabled. DataArray values are replaced with isnull() booleans.")


def is_downloadable(url: str, return_date: bool = False) -> Union[bool, datetime]:
    """Check whether a URL points to a downloadable (non-HTML) resource.

    Issues a HEAD request and inspects the status code and Content-Type.

    Args:
        url: The URL to probe.
        return_date: If True, return the ``Last-Modified`` header as a
            ``datetime`` on success instead of ``True``. Returns ``False``
            when the header is absent or the resource is unavailable.

    Returns:
        ``True`` / ``datetime`` on success, ``False`` otherwise.
    """
    logger.debug("Checking availability of %s", url)
    try:
        h = requests.head(url, allow_redirects=True, timeout=10)
        if h.status_code != 200:
            return False
        if "text/html" in h.headers.get("Content-Type", "").lower():
            return False
        if return_date:
            last_modified = h.headers.get("Last-Modified")
            if last_modified:
                return datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
            return False
        return True
    except requests.exceptions.RequestException as e:
        logger.warning("Availability check failed for %s: %s", url, e)
        return False


def are_downloadable(urls: List[str], return_date: bool = False) -> Union[bool, datetime]:
    """Check whether *all* URLs in a list point to downloadable resources.

    Runs ``is_downloadable`` in parallel via a thread pool.

    Args:
        urls: List of URLs to probe.
        return_date: If True, return the maximum ``Last-Modified`` date across
            all URLs when every URL is available, or ``False`` otherwise.

    Returns:
        ``True`` / ``datetime`` if all URLs are downloadable, ``False`` otherwise.
    """
    with ThreadPoolExecutor() as executor:
        # Utiliser executor.map pour appliquer la fonction is_downloadable à chaque URL
        results = list(executor.map(lambda url: is_downloadable(url, return_date), urls))

    if return_date:
        # Filtrer les résultats pour obtenir uniquement les dates valides
        valid_dates = [result for result in results if isinstance(result, datetime)]
        # Vérifier si toutes les URLs sont téléchargeables et si des dates valides sont présentes
        if len(valid_dates) == len(urls):
            # Renvoie la date maximale
            return max(valid_dates)
        else:
            return False
    else:
        # Renvoie True si toutes les URLs sont téléchargeables, False sinon
        return all(results)
