import xarray as xr


from ._model import Model


class Arome001(Model):
    """Classe pour le modèle AROME à résolution 0.01 degré.

    Regroupement de différents paramètres du modèle atmosphérique français à aire limitée et à haute résolution AROME,
    en fichiers horaires. Données d’analyse et de prévision en points de grille régulière.

    Grille EURW1S100 (55,4N 37,5N 12W 16E) - Pas de temps : 1h.
    """

    groups_ = tuple([f"{h:02d}H" for h in range(52)])
    paquets_ = ("SP1", "SP2", "SP3", "HP1")
    url_ = "https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arome/001/{paquet}/arome__001__{paquet}__{group}__{date}:00:00Z.grib2"
    freq_update = 3

    @staticmethod
    def _process_ds(ds) -> xr.Dataset:
        """Traite un dataset xarray pour le modèle AROME 0.01."""
        ds = ds.expand_dims("valid_time").drop_vars("time").rename(valid_time="time")
        return ds


class Arome0025(Model):
    """Classe pour le modèle AROME à résolution 0.025 degré.

    Regroupement de différents paramètres du modèle atmosphérique français à aire limitée et à haute résolution AROME,
    répartis en plusieurs groupes d’échéances : 00h-06h, 07h-12h, 13h-18h, 19h-24h, 25h-30h, 31h-36h, 37h-42h, 43h-48h et 49h-51h.

    Données d’analyse et de prévision en points de grille régulière.

    Grille EURW1S40 (55,4N 37,5N 12W 16E) - Pas de temps : 1h.
    """

    groups_ = ("00H06H", "07H12H", "13H18H", "19H24H", "25H30H", "31H36H", "37H42H", "43H48H", "49H51H")
    paquets_ = ("SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3")
    url_ = "https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arome/0025/{paquet}/arome__0025__{paquet}__{group}__{date}:00:00Z.grib2"
    freq_update = 3

    @staticmethod
    def _process_ds(ds) -> xr.Dataset:
        """Traite un dataset xarray pour le modèle AROME 0.025."""
        if "time" in ds:
            ds = ds.drop_vars("time")
        if "step" in ds.dims:
            ds = ds.swap_dims(step="valid_time").rename(valid_time="time")
        return ds
