from ._meteo_france import HourlyProcess, MeteoFrance


class MFWAM(MeteoFrance, HourlyProcess):
    base_url_ = "https://object.data.gouv.fr/meteofrance-pnt/pnt"
    paquets_ = ("SP1",)

    past_runs_ = 8
    freq_update = 6


class MFWAM0025(MFWAM):
    """
    https://meteo.data.gouv.fr/datasets/65bd1a505a5b412989a84ca7

    Regroupement de différents paramètres du modèle de prévision de vagues MFWAM.
    Champs d’analyse et de prévision en points de grille.
    Hauteur, direction et période de la mer du vent, de la mer totale et des houles primaire, secondaire et totale.

    Domaine: Zone FRANCE élargie (53N 38N 8W 12E)

    Pas de temps : 1h

    Résolution : 0,025°
    """

    groups_ = tuple([f"{h:03d}H" for h in range(1, 49)])
    url_ = "{date}:00:00Z/vague-surcote/MFWAM/0025/{paquet}/vague-surcote-MFWAM__0025__{paquet}__{group}__{date}:00:00Z.grib2"


class MFWAM01(MFWAM):
    """
    https://meteo.data.gouv.fr/datasets/65bd1a2957e1cc7c9625e7b5

    Regroupement de différents paramètres du modèle de prévision de vagues MFWAM.
    Champs d’analyse et de prévision en points de grille.
    Hauteur, direction et période de la mer du vent, de la mer totale et des houles primaire, secondaire et totale.

    Domaine: Europe (72N 20N 32W 42E) et à partir du 25/03/25 run de 06 Domaine: Globe

    Pas de temps : 1h jusqu'à 48h puis 3h

    Résolution : 0,1°
    """

    groups_ = tuple([f"{h:03d}H" for h in range(1, 49)])
    url_ = (
        "{date}:00:00Z/vague-surcote/MFWAM/01/{paquet}/vague-surcote-MFWAM__01__{paquet}__{group}__{date}:00:00Z.grib2"
    )
