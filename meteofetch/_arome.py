from ._model import HourlyProcess, Model, MultiHourProcess


class Arome001(Model, HourlyProcess):
    """Classe pour le modèle AROME à résolution 0.01 degré.

    Regroupement de différents paramètres du modèle atmosphérique français à aire limitée et à haute résolution AROME,
    en fichiers horaires. Données d’analyse et de prévision en points de grille régulière.

    Grille EURW1S100 (55,4N 37,5N 12W 16E) - Pas de temps : 1h.
    """

    groups_ = tuple([f"{h:02d}H" for h in range(52)])
    paquets_ = ("SP1", "SP2", "SP3", "HP1")
    url_ = "{date}:00:00Z/arome/001/{paquet}/arome__001__{paquet}__{group}__{date}:00:00Z.grib2"
    freq_update = 3


class Arome0025(Model, MultiHourProcess):
    """Classe pour le modèle AROME à résolution 0.025 degré.

    Regroupement de différents paramètres du modèle atmosphérique français à aire limitée et à haute résolution AROME,
    répartis en plusieurs groupes d’échéances : 00h-06h, 07h-12h, 13h-18h, 19h-24h, 25h-30h, 31h-36h, 37h-42h, 43h-48h et 49h-51h.

    Données d’analyse et de prévision en points de grille régulière.

    Grille EURW1S40 (55,4N 37,5N 12W 16E) - Pas de temps : 1h.
    """

    groups_ = ("00H06H", "07H12H", "13H18H", "19H24H", "25H30H", "31H36H", "37H42H", "43H48H", "49H51H")
    paquets_ = ("SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3")
    url_ = "{date}:00:00Z/arome/0025/{paquet}/arome__0025__{paquet}__{group}__{date}:00:00Z.grib2"
    freq_update = 3


class AromeOutreMerAntilles(Model, HourlyProcess):
    """Regroupement de différents paramètres du modèle atmosphérique français à aire limitée à haute résolution AROME sur les Antilles françaises.

    Champs d’analyse et de prévision en points de grille régulière sur le domaine “Antilles”.

    Grille : CARAïBES (9,7N 22,9N 75,3W 51,7W) - Pas de temps : 1h"""

    groups_ = tuple([f"{h:03d}H" for h in range(49)])
    paquets_ = ("SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3")
    url_ = "{date}:00:00Z/arome-om/ANTIL/0025/{paquet}/arome-om-ANTIL__0025__{paquet}__{group}__{date}:00:00Z.grib2"
    freq_update = 3


class AromeOutreMerGuyane(Model, HourlyProcess):
    """Regroupement de différents paramètres du modèle atmosphérique français à aire limitée à haute résolution AROME sur la Guyane.

    Champs d’analyse et de prévision en points de grille régulière sur le domaine “Guyane”.

    Grille : GUYANE - Pas de temps : 1h"""

    groups_ = tuple([f"{h:03d}H" for h in range(49)])
    paquets_ = ("SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3")
    url_ = "{date}:00:00Z/arome-om/GUYANE/0025/{paquet}/arome-om-GUYANE__0025__{paquet}__{group}__{date}:00:00Z.grib2"
    freq_update = 3


class AromeOutreMerIndien(Model, HourlyProcess):
    """Regroupement de différents paramètres du modèle atmosphérique français à aire limitée à haute résolution AROME sur la Réunion-Mayotte.

    Champs d’analyse et de prévision en points de grille régulière sur le domaine “Réunion-Mayotte”.

    Grille : INDIEN (7,25S 25,9S 32,75E 67,6E) - Pas de temps : 1h"""

    groups_ = tuple([f"{h:03d}H" for h in range(49)])
    paquets_ = ("SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3")
    url_ = "{date}:00:00Z/arome-om/INDIEN/0025/{paquet}/arome-om-INDIEN__0025__{paquet}__{group}__{date}:00:00Z.grib2"
    freq_update = 3


class AromeOutreMerNouvelleCaledonie(Model, HourlyProcess):
    """Regroupement de différents paramètres du modèle atmosphérique français à aire limitée à haute résolution AROME sur la Nouvelle-Calédonie.

    Champs d’analyse et de prévision en points de grille régulière sur le domaine “Nouvelle-Calédonie”.

    Grille : NCALED (10S 30S 156E 174E) - Pas de temps : 1h"""

    groups_ = tuple([f"{h:03d}H" for h in range(49)])
    paquets_ = ("SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3")
    url_ = "{date}:00:00Z/arome-om/NCALED/0025/{paquet}/arome-om-NCALED__0025__{paquet}__{group}__{date}:00:00Z.grib2"
    freq_update = 3


class AromeOutreMerPolynesie(Model, HourlyProcess):
    """Regroupement de différents paramètres du modèle atmosphérique français à aire limitée à haute résolution AROME sur la Polynésie.

    Champs d’analyse et de prévision en points de grille régulière sur le domaine “Polynésie”.

    Grille : POLYN (12,6S 25,25S 157,5W 144,5W) - Pas de temps : 1h"""

    groups_ = tuple([f"{h:03d}H" for h in range(49)])
    paquets_ = ("SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3")
    url_ = "{date}:00:00Z/arome-om/POLYN/0025/{paquet}/arome-om-POLYN__0025__{paquet}__{group}__{date}:00:00Z.grib2"
    freq_update = 3
