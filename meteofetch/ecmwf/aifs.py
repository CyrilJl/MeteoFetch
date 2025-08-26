from . import ECMWF


class Aifs(ECMWF):
    """ECMWF’s fully data-driven weather forecast model.

    Classe de récupération des données forecast opérationnelles AIFS
    https://www.ecmwf.int/en/forecasts/datasets/open-data
    """

    base_url_ = "https://data.ecmwf.int/forecasts"
    past_runs_ = 8
    freq_update = 6
    url_ = "{ymd}/{hour}z/aifs-single/0p25/oper/{ymd}{hour}0000-{group}h-oper-fc.grib2"
    groups_ = tuple(range(0, 246, 6))
