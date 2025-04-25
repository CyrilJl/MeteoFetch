"""
The Well Known Text of WGS 84 is hardcoded in the code to avoid having to import pyproj.
"""

import os
from pathlib import Path
from typing import Literal

import eccodes
import requests
import xarray as xr

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


def set_grib_defs(source: Literal["eccodes", "meteofrance"]):
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
            os.environ["ECCODES_DEFINITION_PATH"] = required_path
        print(f"Définitions GRIB mises à jour : {source}")
        eccodes.codes_context_delete()


def set_test_mode():
    os.environ["meteofetch_test_mode"] = "1"
    print("Mode test activé. Les données des xr.DataArrays sont transformés en booléens par isnull().")


def is_downloadable(url) -> bool:
    try:
        h = requests.head(url, allow_redirects=True, timeout=10)
        # Vérifier le code de statut
        if not h.status_code == 200:
            return False
        # Vérifier le Content-Type - exclure les pages HTML par exemple
        content_type = h.headers.get("Content-Type", "")
        if "text/html" in content_type.lower():
            return False
        # Vérifier Content-Length (optionnel)
        content_length = h.headers.get("Content-Length")
        if content_length and int(content_length) > 0:
            return True
        # Si Content-Length n'est pas disponible, on se base sur Content-Disposition
        content_disposition = h.headers.get("Content-Disposition", "")
        if "attachment" in content_disposition.lower() or "filename" in content_disposition.lower():
            return True
        return True

    except requests.exceptions.RequestException:
        return False
