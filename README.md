# MeteoFetch

``MeteoFetch`` permet de récuopérer les dernières prévisions modèles MétéoFrance Arome 0.025° et 0.01° **sans clé d'API**.
Les prévisions sont renvoyés sous forme de ``xarray.DataArray``. Le package est en cours de développement.

Plus de précisions sur https://meteo.data.gouv.fr/.

## Installation

```console
pip install meteofetch
```

## Usage

```python
from meteofetch import Arome0025

datasets = Arome0025.get_latest_forecast(paquet='SP3')
datasets['ssr']
```

Par défaut, ``meteofetch`` sert à l'utilisateur toutes les variables contenues dans le paquet requêté.
Il est cependant conseillée de préciser les variables voulues pour limiter l'usage mémoire :

```python
from meteofetch import Arome001

datasets = Arome001.get_latest_forecast(paquet='SP1', variables=('u10', 'v10'))
datasets['u10']

datasets = Arome001.get_latest_forecast(paquet='SP2', variables='sp')
datasets['t']
```

### Nomenclature

### Arome 0.01°

Résumé des champs contenus dans chaque paquet requêtable pour Arome 0.01° :

| Paquet | Champ | Description | Dimensions | Shape d'un run complet|
|--------|-------|-------------|------------|-------|
| SP1    | u10   | 10 metre U wind component | (time, latitude, longitude) | (52, 1791, 2801) |
|        | v10   | 10 metre V wind component | (time, latitude, longitude) | (52, 1791, 2801) |
|        | t2m   | 2 metre temperature | (time, latitude, longitude) | (52, 1791, 2801) |
|        | r2    | 2 metre relative humidity | (time, latitude, longitude) | (52, 1791, 2801) |
|        | efg10 | 10 metre eastward wind gust since previous post-processing | (time, latitude, longitude) | (51, 1791, 2801) |
|        | nfg10 | 10 metre northward wind gust since previous post-processing | (time, latitude, longitude) | (51, 1791, 2801) |
| SP2    | sp    | Surface pressure | (time, latitude, longitude) | (52, 1791, 2801) |
|        | CAPE_INS | Convective Available Potential Energy instantaneous | (time, latitude, longitude) | (52, 1791, 2801) |
|        | lcc   | Low cloud cover | (time, latitude, longitude) | (51, 1791, 2801) |
|        | mcc   | Medium cloud cover | (time, latitude, longitude) | (51, 1791, 2801) |
|        | hcc   | High cloud cover | (time, latitude, longitude) | (51, 1791, 2801) |
|        | tgrp  | Graupel (snow pellets) precipitation | (time, latitude, longitude) | (51, 1791, 2801) |
|        | tirf  | Time integral of rain flux | (time, latitude, longitude) | (51, 1791, 2801) |
|        | tsnowp | Total snow precipitation | (time, latitude, longitude) | (51, 1791, 2801) |
| SP3    | h     | Geometrical height | (latitude, longitude) | (1791, 2801) |
| HP1    | ws    | Wind speed | (time, heightAboveGround, latitude, longitude) | (52, 2, 1791, 2801) |
|        | u     | U component of wind | (time, heightAboveGround, latitude, longitude) | (52, 2, 1791, 2801) |
|        | v     | V component of wind | (time, heightAboveGround, latitude, longitude) | (52, 2, 1791, 2801) |
|        | r     | Relative humidity | (time, heightAboveGround, latitude, longitude) | (52, 4, 1791, 2801) |
|        | u10   | 10 metre U wind component | (time, latitude, longitude) | (52, 1791, 2801) |
|        | v10   | 10 metre V wind component | (time, latitude, longitude) | (52, 1791, 2801) |
|        | si10  | 10 metre wind speed | (time, latitude, longitude) | (52, 1791, 2801) |
|        | wdir10 | 10 metre wind direction | (time, latitude, longitude) | (52, 1791, 2801) |
|        | wdir  | Wind direction | (time, heightAboveGround, latitude, longitude) | (52, 3, 1791, 2801) |
|        | u100  | 100 metre U wind component | (time, latitude, longitude) | (52, 1791, 2801) |
|        | v100  | 100 metre V wind component | (time, latitude, longitude) | (52, 1791, 2801) |
|        | si100 | 100 metre wind speed | (time, latitude, longitude) | (52, 1791, 2801) |

### Arome 0.025°

Résumé des champs contenus dans chaque paquet requêtable pour Arome 0.025° :

| Paquet | Champ       | Description                                                                 | Dimensions                                      | Shape d'un run complet              |
|--------|-------------|-----------------------------------------------------------------------------|------------------------------------------------|---------------------|
| SP1    | fg10        | Maximum 10 metre wind gust since previous post-processing                   | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | efg10       | 10 metre eastward wind gust since previous post-processing                  | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | nfg10       | 10 metre northward wind gust since previous post-processing                 | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | u10         | 10 metre U wind component                                                   | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | v10         | 10 metre V wind component                                                   | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | si10        | 10 metre wind speed                                                         | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | wdir10      | 10 metre wind direction                                                     | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | t2m         | 2 metre temperature                                                         | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | r2          | 2 metre relative humidity                                                   | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | prmsl       | Pressure reduced to MSL                                                     | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | ssrd        | Surface short-wave (solar) radiation downwards                              | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | tp          | Total Precipitation                                                         | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | tgrp        | Graupel (snow pellets) precipitation                                        | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | tsnowp      | Total snow precipitation                                                    | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP2    | d2m         | 2 metre dewpoint temperature                                                | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | sh2         | 2 metre specific humidity                                                   | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | mx2t        | Maximum temperature at 2 metres since previous post-processing              | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | mn2t        | Minimum temperature at 2 metres since previous post-processing              | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | t           | Temperature                                                                 | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | sp          | Surface pressure                                                            | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | blh         | Boundary layer height                                                       | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | h           | Geometrical height                                                          | (latitude, longitude)                      | (717, 1121)         |
|        | lcc         | Low cloud cover                                                             | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | mcc         | Medium cloud cover                                                          | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | hcc         | High cloud cover                                                            | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | tirf        | Time integral of rain flux                                                  | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | CAPE_INS    | Convective Available Potential Energy instantaneous                         | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP3    | sshf        | Time-integrated surface sensible heat net flux                              | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | slhf        | Time-integrated surface latent heat net flux                                | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | strd        | Surface long-wave (thermal) radiation downwards                             | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | ssr         | Surface net short-wave (solar) radiation                                    | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | str         | Surface net long-wave (thermal) radiation                                   | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | ssrc        | Surface net short-wave (solar) radiation, clear sky                         | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | strc        | Surface net long-wave (thermal) radiation, clear sky                        | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | iews        | Instantaneous eastward turbulent surface stress                             | (time, latitude, longitude)              | (51, 717, 1121)     |
|        | inss        | Instantaneous northward turbulent surface stress                            | (time, latitude, longitude)              | (51, 717, 1121)     |
| IP1    | z           | Geopotential                                                                | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | t           | Temperature                                                                 | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | u           | U component of wind                                                         | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | v           | V component of wind                                                         | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | r           | Relative humidity                                                           | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
| IP2    | crwc        | Specific rain water content                                                 | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | cswc        | Specific snow water content                                                 | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | clwc        | Specific cloud liquid water content                                         | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | ciwc        | Specific cloud ice water content                                            | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | cc          | Fraction of cloud cover                                                     | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
| IP3    | ws          | Wind speed                                                                  | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | pv          | Potential vorticity                                                         | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | q           | Specific humidity                                                           | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | w           | Vertical velocity                                                           | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | dpt         | Dew point temperature                                                       | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | wdir        | Wind direction                                                              | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
|        | wz          | Geometric vertical velocity                                                 | (time, isobaricInhPa, latitude, longitude) | (52, 24, 717, 1121) |
| IP4    | tke         | Turbulent kinetic energy                                                    | (time, isobaricInhPa, latitude, longitude) | (51, 24, 717, 1121) |
| IP5    | vo          | Vorticity (relative)                                                        | (time, isobaricInhPa, latitude, longitude) | (52, 5, 717, 1121)  |
|        | absv        | Absolute vorticity                                                          | (time, isobaricInhPa, latitude, longitude) | (52, 5, 717, 1121)  |
|        | papt        | Pseudo-adiabatic potential temperature                                      | (time, isobaricInhPa, latitude, longitude) | (52, 20, 717, 1121) |
|        | z           | Geopotential                                                                | (time, potentialVorticity, latitude, longitude) | (52, 2, 717, 1121)  |
|        | u           | U component of wind                                                         | (time, potentialVorticity, latitude, longitude) | (52, 2, 717, 1121)  |
|        | v           | V component of wind                                                         | (time, potentialVorticity, latitude, longitude) | (52, 2, 717, 1121)  |
| HP1    | ws          | Wind speed                                                                  | (time, heightAboveGround, latitude, longitude) | (52, 22, 717, 1121) |
|        | u           | U component of wind                                                         | (time, heightAboveGround, latitude, longitude) | (52, 22, 717, 1121) |
|        | v           | V component of wind                                                         | (time, heightAboveGround, latitude, longitude) | (52, 22, 717, 1121) |
|        | pres        | Pressure                                                                    | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
|        | t           | Temperature                                                                 | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
|        | r           | Relative humidity                                                           | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
|        | u10         | 10 metre U wind component                                                   | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | v10         | 10 metre V wind component                                                   | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | si10        | 10 metre wind speed                                                         | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | wdir10      | 10 metre wind direction                                                     | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | wdir        | Wind direction                                                              | (time, heightAboveGround, latitude, longitude) | (52, 24, 717, 1121) |
|        | u200        | 200 metre U wind component                                                  | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | v200        | 200 metre V wind component                                                  | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | si200       | 200 metre wind speed                                                        | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | u100        | 100 metre U wind component                                                  | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | v100        | 100 metre V wind component                                                  | (time, latitude, longitude)              | (52, 717, 1121)     |
|        | si100       | 100 metre wind speed                                                        | (time, latitude, longitude)              | (52, 717, 1121)     |
| HP2    | crwc        | Specific rain water content                                                 | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
|        | cswc        | Specific snow water content                                                 | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
|        | z           | Geopotential                                                                | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
|        | q           | Specific humidity                                                           | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
|        | clwc        | Specific cloud liquid water content                                         | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
|        | ciwc        | Specific cloud ice water content                                            | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
|        | cc          | Fraction of cloud cover                                                     | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
|        | dpt         | Dew point temperature                                                       | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
|        | tke         | Turbulent kinetic energy                                                    | (time, heightAboveGround, latitude, longitude) | (51, 25, 717, 1121) |
