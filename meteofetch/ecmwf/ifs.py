from . import ECMWF


class Ifs(ECMWF):
    """Classe de récupération des données forecast opérationnelles ECMWF
    https://www.ecmwf.int/en/forecasts/datasets/open-data
    """

    base_url_ = "https://data.ecmwf.int/forecasts"
    past_runs_ = 8
    freq_update = 12
    url_ = "{ymd}/{hour}z/ifs/0p25/oper/{ymd}{hour}0000-{group}h-oper-fc.grib2"
    groups_ = tuple(range(0, 146, 3)) + tuple(range(150, 366, 6))
