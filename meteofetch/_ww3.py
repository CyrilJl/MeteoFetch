from ._meteo_france import MeteoFrance


class WW3MARO01(MeteoFrance):
    groups_ = ("000H999H",)
    paquets_ = ("SP1",)
    url_ = (
        "{date}:00:00Z/vague-surcote/WW3-MARO/001/{paquet}/vague-surcote-WW3-MARO__001__SP1__{group}__{date}:00:00Z.nc"
    )
    freq_update = 3

    def _process_ds(ds):
        return ds
