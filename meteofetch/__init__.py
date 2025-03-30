import importlib
import os
import sys
from pathlib import Path

# Définition du chemin vers les définitions de grib
# Config eccodes pour le module cfgrib
# Téléchargée depuis https://donneespubliques.meteofrance.fr/donnees_libres/Static/gribdefs_20220126.tar.gz
os.environ["ECCODES_DEFINITION_PATH"] = str(Path(__file__).parent / "gribdefs")

# Recharger le module cfgrib et xarray si déjà importé
# Afin que la redéfinition de la variable d'environnement soit prise en compte
if "cfgrib" in sys.modules:
    importlib.reload(sys.modules["cfgrib"])
    importlib.reload(sys.modules["xarray"])


from ._arome import (
    Arome001,
    Arome0025,
    AromeOutreMerAntilles,
    AromeOutreMerGuyane,
    AromeOutreMerIndien,
    AromeOutreMerNouvelleCaledonie,
    AromeOutreMerPolynesie,
)
from ._arpege import Arpege01, Arpege025

__all__ = [
    "Arome001",
    "Arome0025",
    "AromeOutreMerAntilles",
    "AromeOutreMerGuyane",
    "AromeOutreMerIndien",
    "AromeOutreMerNouvelleCaledonie",
    "AromeOutreMerPolynesie",
    "Arpege01",
    "Arpege025",
]
