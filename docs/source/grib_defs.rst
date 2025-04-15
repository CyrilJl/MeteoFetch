Décodage GRIB
=============

Introduction aux fichiers GRIB
------------------------------

Les fichiers GRIB (GRIdded Binary) sont un format standardisé pour stocker et échanger des données météorologiques. MeteoFrance fournit ses prévisions sous ce format.

Décodage avec ecCodes
---------------------

Le décodage des fichiers GRIB est réalisé par la bibliothèque **ecCodes**, développée par l'ECMWF (European Centre for Medium-Range Weather Forecasts):

* ecCodes inclut des tables de description intégrées qui permettent de décoder la plupart des champs GRIB standard
* Ces tables contiennent les métadonnées nécessaires (noms, unités, descriptions) pour interpréter les données binaires

Limitations des tables standard
-------------------------------

Cependant, les tables standard d'ecCodes présentent certaines limitations avec les fichiers de MeteoFrance:

1. **Couverture incomplète**: Certains champs spécifiques à MeteoFrance ne sont pas décodés
2. **Noms génériques**: Certaines variables peuvent avoir des identifiants trop peu explicites

Solution: les définitions GRIB de MeteoFrance
---------------------------------------------

MeteoFrance fournit un fichier complémentaire de définitions GRIB (``grib_defs``) qui:

* Étend la couverture des champs: Permet de décoder davantage de variables spécifiques
* Améliore les noms: Certains champs obtiennent des libellés plus précis

Activation des définitions MeteoFrance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le choix entre les définitions **ecCodes** (par défaut) et **MeteoFrance** se fait via un simple switch::

    import meteofetch

    # Mode par défaut (tables ecCodes standard)
    meteofetch.set_grib_defs('eccodes')

    # Mode MeteoFrance (définitions étendues)
    meteofetch.set_grib_defs('meteofrance')

Conséquences de l'utilisation des grib_defs de MeteoFrance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

L'activation des définitions MeteoFrance modifie le comportement de décodage:

Avantages:
^^^^^^^^^^
* **Plus de champs disponibles**: Accès à des variables supplémentaires non reconnues par ecCodes
* **Noms plus explicites**: Certaines variables sont renommées pour une meilleure lisibilité

Inconvénients:
^^^^^^^^^^^^^^
* **Moins de métadonnées**:

  - Les unités peuvent être absentes
  - Les descriptions (``long_name``) sont parfois manquantes
  - Les ``xarray.DataArray`` produits peuvent donc être moins documentés

Évolutions futures
------------------

MeteoFrance a indiqué que des **définitions GRIB plus complètes** devraient être publiées, incluant davantage de métadonnées (unités, descriptions). Cependant, aucun délai précis n'a été communiqué.

Recommandations
---------------

Le choix entre ``'eccodes'`` et ``'meteofrance'`` dépend des besoins:

* **Pour une exploitation standard** (noms cohérents, métadonnées complètes) → ``set_grib_defs('eccodes')``
* **Pour accéder à tous les champs** (quitte à avoir moins de descriptions) → ``set_grib_defs('meteofrance')``

Une approche hybride (basculer entre les deux modes selon les besoins) peut aussi être envisagée.