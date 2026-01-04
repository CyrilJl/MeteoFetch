<div align="center">

[![PyPI - Version](https://img.shields.io/pypi/v/meteofetch)](https://pypi.org/project/meteofetch/)
[![conda-forge](https://anaconda.org/conda-forge/meteofetch/badges/version.svg)](https://anaconda.org/conda-forge/meteofetch)
[![Documentation Status](https://img.shields.io/readthedocs/meteofetch?logo=read-the-docs)](https://meteofetch.readthedocs.io)
[![Unit tests](https://github.com/CyrilJl/meteofetch/actions/workflows/pytest.yml/badge.svg)](https://github.com/CyrilJl/meteofetch/actions/workflows/pytest.yml)

  <a href="https://github.com/CyrilJl/meteofetch">
    <img src="https://raw.githubusercontent.com/CyrilJl/MeteoFetch/main/_static/logo.svg" alt="Logo" width="250"/>
  </a>

</div>

MeteoFetch est un client Python pour récupérer, sans clé API, des prévisions Météo-France (Arome, Arpege, MFWAM) et ECMWF (IFS open data).

Forces
- Sans clé API, accès direct aux jeux de données ouverts.
- Choix du modèle, du paquet et des variables pour limiter la mémoire.
- Retour en `xarray` (DataArray) prêt pour analyse/plot.

Installation
```console
pip install meteofetch
```
```console
conda install -c conda-forge meteofetch
```
```console
mamba install meteofetch
```

Un modèle représente une source et une résolution (ex: Arome0025, Arpege01, Ifs). Un paquet regroupe des variables prédéfinies téléchargeables en une fois (ex: SP1, SP2, SP3). Vous pouvez aussi demander des variables précises pour un paquet.

Vidéo de carte avec mapflow
```python
from mapflow import animate
from meteofetch import Arome0025

datasets = Arome0025.get_latest_forecast(paquet="SP1")
animate(da=datasets["t2m"], path="run_t2m.mp4")
```

https://github.com/user-attachments/assets/05dec9f8-de94-4f22-bb25-2e55da4fb768

Documentation: https://meteofetch.readthedocs.io
