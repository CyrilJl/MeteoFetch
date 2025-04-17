meteofetch
==========

``meteofetch`` est un package qui permet de récupérer les dernières prévisions de MétéoFrance et de l'ECMWF. Ces modèles sont
disponibles en open data **sans clé d'API**. La plus-value de ce package est la simplicité d'utilisation, la flexibilité (récupération
des fichiers grib sur disque ou chargement en mémoire des champs souhaités sous forme de ``xr.DataArray``), ainsi que cette documentation
qui propose une description des champs qui sont requêtables pour chaque modèle.

``meteofetch`` s'installe facilement depuis Pypi :

.. code-block:: console

   pip install pypi

Ou bien depuis conda-forge :

.. code-block:: console

   conda install -y -c conda-forge meteofetch

.. code-block:: console

   mamba install -y meteofetch

.. toctree::
   :maxdepth: 1
   :hidden:
   
   usage
   models
   grib_defs

