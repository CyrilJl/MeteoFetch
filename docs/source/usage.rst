:notoc: true

.. _usage:

En pratique
###########

Utilisation
-----------

``meteofetch`` propose deux modes de fonctionnement :

- un où les fichiers gribs sont enregistrés dans le ``path`` du choix de l'utilisateur

  .. code-block:: python

    from meteofetch import Arpege01

    path = 'your/folder/'

    paths = Arpege01.get_latest_forecast(paquet='SP1', path=path, return_data=False)

- un où les fichiers gribs sont téléchargés dans un dossier temporaire et où les variables souhaitées
  par l'utilisateurs sont renvoyées (mode par défaut)

  .. code-block:: python

    from meteofetch import Arome0025

    datasets = Arome0025.get_latest_forecast(paquet='SP2')
    datasets.keys()
    # dict_keys(['d2m', 'sh2', 'mx2t', 'mn2t', 't', 'sp', 'blh', 'h', 'lcc', 'mcc', 'hcc', 'tirf', 'CAPE_INS'])


  .. code-block:: python

    from meteofetch import Arome0025

    datasets = Arome0025.get_latest_forecast(paquet='SP2', variables=('t', 'sp', 'h'))
    datasets.keys()
    # dict_keys(['t', 'sp', 'h'])



Disponibilité
-------------

Il est également possible de vérifier la disponibilité des derniers runs de prévision pour un modèle donné.

.. code-block:: python

  from meteofetch import Arome0025

  Arome0025.availability()

.. code-block:: text

  |                     |   SP1 |   SP2 |   SP3 |   IP1 |   IP2 |   IP3 |   IP4 |   IP5 |   HP1 |   HP2 |   HP3 |
  |:--------------------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
  | 2024-05-21 18:00:00 |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |
  | 2024-05-21 15:00:00 |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |
  | 2024-05-21 12:00:00 |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |
  | 2024-05-21 09:00:00 |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |
  | 2024-05-21 06:00:00 |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |
  | 2024-05-21 03:00:00 |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |
  | 2024-05-21 00:00:00 |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |
  | 2024-05-20 21:00:00 |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |  True |

Ou de récupérer la date du dernier run de prévision disponible pour un paquet donné.

.. code-block:: python

  from meteofetch import Arome0025

  Arome0025.get_latest_forecast_time(paquet="SP1")

.. code-block:: text

  Timestamp('2024-05-21 18:00:00+0000', tz='UTC')
