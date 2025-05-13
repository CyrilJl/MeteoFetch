Utilisation
===========

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



Vous pouvez également appeler la méthode ``availability``, pour avoir une meilleure idée de la disponibilité des derniers runs :

.. code-block:: python

  from meteofetch import Arpege025

  Arpege025.availability()

  #                        SP1    SP2    IP1    IP2    IP3    IP4    HP1    HP2
  # 2025-05-13 12:00:00  False  False  False  False  False  False  False  False
  # 2025-05-13 06:00:00   True   True   True   True   True   True   True   True
  # 2025-05-13 00:00:00   True   True   True   True   True   True   True   True
  # 2025-05-12 18:00:00   True   True   True   True   True   True   True   True
  # 2025-05-12 12:00:00   True   True   True   True   True   True   True   True
  # 2025-05-12 06:00:00   True   True   True   True   True   True   True   True
  # 2025-05-12 00:00:00   True   True   True   True   True   True   True   True
  # 2025-05-11 18:00:00   True   True   True   True   True   True   True   True
