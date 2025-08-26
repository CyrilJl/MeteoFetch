from . import ecmwf, meteofrance
from ._misc import set_grib_defs, set_test_mode
from .ecmwf import ECMWF
from .ecmwf.aifs import Aifs
from .ecmwf.ifs import Ifs
from .meteofrance import HourlyProcess, MeteoFrance, MultiHourProcess
from .meteofrance.arome import (
    Arome001,
    Arome0025,
    AromeOutreMer,
    AromeOutreMerAntilles,
    AromeOutreMerGuyane,
    AromeOutreMerIndien,
    AromeOutreMerNouvelleCaledonie,
    AromeOutreMerPolynesie,
)
from .meteofrance.arpege import Arpege01, Arpege025
from .meteofrance.mfwam import MFWAM0025, MFWAM01

__all__ = [
    "ecmwf",
    "meteofrance",
    "set_grib_defs",
    "set_test_mode",
    "ECMWF",
    "Aifs",
    "Ifs",
    "MeteoFrance",
    "HourlyProcess",
    "MultiHourProcess",
    "Arome001",
    "Arome0025",
    "AromeOutreMer",
    "AromeOutreMerAntilles",
    "AromeOutreMerGuyane",
    "AromeOutreMerIndien",
    "AromeOutreMerNouvelleCaledonie",
    "AromeOutreMerPolynesie",
    "Arpege01",
    "Arpege025",
    "MFWAM0025",
    "MFWAM01",
]
