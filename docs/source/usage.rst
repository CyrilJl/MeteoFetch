Utilisation
===========

``meteofetch`` propose deux modes de fonctionnement :

- un où les fichiers gribs sont enregistrés dans le ``path`` du choix de l'utilisateur,
- un où les fichiers gribs sont téléchargés dans un dossier temporaire et où les variables souhaitées
  par l'utilisateurs sont renvoyées (mode par défaut)

  .. code-block:: python

    from meteofetch import Arome025

    datasets = Arome025.get_latest_forecast(paquet='SP2')
    datasets.keys()


  .. code-block:: python

    from meteofetch import Arome025

    datasets = Arome025.get_latest_forecast(paquet='SP2', variables=('t', 'sp', 'h'))
    datasets.keys()

  .. code-block:: python

    from meteofetch import Arpege01

    path = 'your/folder/'

    paths = Arpege01.get_latest_forecast(paquet='SP1', path=path, return_data=False)