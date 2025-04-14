from ._meteo_france import MeteoFrance, MultiHourProcess


class Arpege01(MeteoFrance, MultiHourProcess):
    """Classe pour le modèle ARPEGE à résolution 0.1 degré.

    Regroupement de différents paramètres du modèle français de prévision atmosphérique global Arpège, répartis en plusieurs groupes d’échéances : 00h-12h, 13h-24h, 25h-36h, 37h-48h, 49h-60h, 61h-72h, 73h-84h, 85h-96h et 97h-102h.

    Données d’analyse et de prévision en points de grille régulière.

    Grille EURAT01 (72N 20N 32W 42E) - Pas de temps : 1h puis 3h
    """

    groups_ = (
        "000H012H",
        "013H024H",
        "025H036H",
        "037H048H",
        "049H060H",
        "061H072H",
        "073H084H",
        "085H096H",
        "097H102H",
    )
    paquets_ = ("SP1", "SP2", "IP1", "IP2", "IP3", "IP4", "HP1", "HP2")
    url_ = "{date}:00:00Z/arpege/01/{paquet}/arpege__01__{paquet}__{group}__{date}:00:00Z.grib2"
    freq_update = 6


class Arpege025(MeteoFrance, MultiHourProcess):
    """Classe pour le modèle ARPEGE à résolution 0.25 degré.

    Regroupement de différents paramètres du modèle français de prévision atmosphérique global Arpège, répartis en 4 groupes d'échéances : 00h-24h, 25h-48h, 49h-72h et 73h-102h.

    Données d’analyse et de prévision en points de grille régulière.

    Grille GLOB025 (53N 38N 8W 12E) - Pas de temps : 1h puis 3h
    """

    groups_ = ("000H024H", "025H048H", "049H072H", "073H102H")
    paquets_ = ("SP1", "SP2", "IP1", "IP2", "IP3", "IP4", "HP1", "HP2")
    url_ = "{date}:00:00Z/arpege/025/{paquet}/arpege__025__{paquet}__{group}__{date}:00:00Z.grib2"
    freq_update = 6
