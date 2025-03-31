import os
from pathlib import Path

import eccodes

# Définition du chemin vers les définitions de grib
# Config eccodes pour le module cfgrib
# Téléchargée depuis https://donneespubliques.meteofrance.fr/donnees_libres/Static/gribdefs_20220126.tar.gz
os.environ["ECCODES_DEFINITION_PATH"] = str(Path(__file__).parent / "gribdefs")
# Permet de recharger la librairie binaire eccodes pour que la variable d'environnement
# soit prise en compte
eccodes.codes_context_delete()


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
