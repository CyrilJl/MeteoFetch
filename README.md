# MeteoFetch

Récupération des prévisions modèles MétéoFrance Arome 0.025° et 0.01° **sans clé d'API**.

## Usage

```python
from meteofetch import Arome0025

datasets = Arome0025.get_latest_forecast(paquet='SP3')
datasets['ssr'].isel(time=5).plot(cmap='Spectral_r')
```

### Nomenclature

### Arome 0.01°

Résumé des champs contenus dans chaque paquet requêtable pour Arome 0.01° :

| Paquet | Champ | Description | Dimensions | Shape d'un run complet|
|--------|-------|-------------|------------|-------|
| SP1    | u10   | 10 metre U wind component | (time, latitude, longitude) | (52, 1791, 2801) |
| SP1    | v10   | 10 metre V wind component | (time, latitude, longitude) | (52, 1791, 2801) |
| SP1    | t2m   | 2 metre temperature | (time, latitude, longitude) | (52, 1791, 2801) |
| SP1    | r2    | 2 metre relative humidity | (time, latitude, longitude) | (52, 1791, 2801) |
| SP1    | efg10 | 10 metre eastward wind gust since previous post-processing | (time, latitude, longitude) | (51, 1791, 2801) |
| SP1    | nfg10 | 10 metre northward wind gust since previous post-processing | (time, latitude, longitude) | (51, 1791, 2801) |
| SP2    | sp    | Surface pressure | (time, latitude, longitude) | (52, 1791, 2801) |
| SP2    | CAPE_INS | Convective Available Potential Energy instantaneous | (time, latitude, longitude) | (52, 1791, 2801) |
| SP2    | lcc   | Low cloud cover | (time, latitude, longitude) | (51, 1791, 2801) |
| SP2    | mcc   | Medium cloud cover | (time, latitude, longitude) | (51, 1791, 2801) |
| SP2    | hcc   | High cloud cover | (time, latitude, longitude) | (51, 1791, 2801) |
| SP2    | tgrp  | Graupel (snow pellets) precipitation | (time, latitude, longitude) | (51, 1791, 2801) |
| SP2    | tirf  | Time integral of rain flux | (time, latitude, longitude) | (51, 1791, 2801) |
| SP2    | tsnowp | Total snow precipitation | (time, latitude, longitude) | (51, 1791, 2801) |
| SP3    | h     | Geometrical height | (latitude, longitude) | (1791, 2801) |
| HP1    | ws    | Wind speed | (time, heightAboveGround, latitude, longitude) | (52, 2, 1791, 2801) |
| HP1    | u     | U component of wind | (time, heightAboveGround, latitude, longitude) | (52, 2, 1791, 2801) |
| HP1    | v     | V component of wind | (time, heightAboveGround, latitude, longitude) | (52, 2, 1791, 2801) |
| HP1    | r     | Relative humidity | (time, heightAboveGround, latitude, longitude) | (52, 4, 1791, 2801) |
| HP1    | u10   | 10 metre U wind component | (time, latitude, longitude) | (52, 1791, 2801) |
| HP1    | v10   | 10 metre V wind component | (time, latitude, longitude) | (52, 1791, 2801) |
| HP1    | si10  | 10 metre wind speed | (time, latitude, longitude) | (52, 1791, 2801) |
| HP1    | wdir10 | 10 metre wind direction | (time, latitude, longitude) | (52, 1791, 2801) |
| HP1    | wdir  | Wind direction | (time, heightAboveGround, latitude, longitude) | (52, 3, 1791, 2801) |
| HP1    | u100  | 100 metre U wind component | (time, latitude, longitude) | (52, 1791, 2801) |
| HP1    | v100  | 100 metre V wind component | (time, latitude, longitude) | (52, 1791, 2801) |
| HP1    | si100 | 100 metre wind speed | (time, latitude, longitude) | (52, 1791, 2801) |

### Arome 0.025°

Résumé des champs contenus dans chaque paquet requêtable pour Arome 0.025° :

| Paquet | Champ       | Description                                                                 | Dimensions                                      | Shape d'un run complet              |
|--------|-------------|-----------------------------------------------------------------------------|------------------------------------------------|---------------------|
| SP1    | fg10        | Maximum 10 metre wind gust since previous post-processing                   | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP1    | efg10       | 10 metre eastward wind gust since previous post-processing                  | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP1    | nfg10       | 10 metre northward wind gust since previous post-processing                 | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP1    | u10         | 10 metre U wind component                                                   | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP1    | v10         | 10 metre V wind component                                                   | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP1    | si10        | 10 metre wind speed                                                         | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP1    | wdir10      | 10 metre wind direction                                                     | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP1    | t2m         | 2 metre temperature                                                         | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP1    | r2          | 2 metre relative humidity                                                   | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP1    | prmsl       | Pressure reduced to MSL                                                     | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP1    | ssrd        | Surface short-wave (solar) radiation downwards                              | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP1    | tp          | Total Precipitation                                                         | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP1    | tgrp        | Graupel (snow pellets) precipitation                                        | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP1    | tsnowp      | Total snow precipitation                                                    | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP2    | d2m         | 2 metre dewpoint temperature                                                | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP2    | sh2         | 2 metre specific humidity                                                   | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP2    | mx2t        | Maximum temperature at 2 metres since previous post-processing              | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP2    | mn2t        | Minimum temperature at 2 metres since previous post-processing              | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP2    | t           | Temperature                                                                 | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP2    | sp          | Surface pressure                                                            | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP2    | blh         | Boundary layer height                                                       | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP2    | h           | Geometrical height                                                          | (latitude, longitude)                      | (717, 1121)         |
| SP2    | lcc         | Low cloud cover                                                             | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP2    | mcc         | Medium cloud cover                                                          | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP2    | hcc         | High cloud cover                                                            | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP2    | tirf        | Time integral of rain flux                                                  | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP2    | CAPE_INS    | Convective Available Potential Energy instantaneous                         | (time, latitude, longitude)              | (52, 717, 1121)     |
| SP3    | sshf        | Time-integrated surface sensible heat net flux                              | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP3    | slhf        | Time-integrated surface latent heat net flux                                | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP3    | strd        | Surface long-wave (thermal) radiation downwards                             | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP3    | ssr         | Surface net short-wave (solar) radiation                                    | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP3    | str         | Surface net long-wave (thermal) radiation                                   | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP3    | ssrc        | Surface net short-wave (solar) radiation, clear sky                         | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP3    | strc        | Surface net long-wave (thermal) radiation, clear sky                        | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP3    | iews        | Instantaneous eastward turbulent surface stress                             | (time, latitude, longitude)              | (51, 717, 1121)     |
| SP3    | inss        | Instantaneous northward turbulent surface stress                            | (time, latitude, longitude)              | (51, 717, 1121)     |
| IP1    | z           | Geopotential                                                                | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP1    | t           | Temperature                                                                 | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP1    | u           | U component of wind                                                         | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP1    | v           | V component of wind                                                         | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP1    | r           | Relative humidity                                                           | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP2    | crwc        | Specific rain water content                                                 | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP2    | cswc        | Specific snow water content                                                 | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP2    | clwc        | Specific cloud liquid water content                                         | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP2    | ciwc        | Specific cloud ice water content                                            | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP2    | cc          | Fraction of cloud cover                                                     | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP3    | ws          | Wind speed                                                                  | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP3    | pv          | Potential vorticity                                                         | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP3    | q           | Specific humidity                                                           | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP3    | w           | Vertical velocity                                                           | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP3    | dpt         | Dew point temperature                                                       | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP3    | wdir        | Wind direction                                                              | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP3    | wz          | Geometric vertical velocity                                                 | (time, 'isobaricInhPa', latitude, longitude) | (52, 24, 717, 1121) |
| IP4    | tke         | Turbulent kinetic energy                                                    | (time, 'isobaricInhPa', latitude, longitude) | (51, 24, 717, 1121) |
| IP5    | vo          | Vorticity (relative)                                                        | (time, 'isobaricInhPa', latitude, longitude) | (52, 5, 717, 1121)  |
| IP5    | absv        | Absolute vorticity                                                          | (time, 'isobaricInhPa', latitude, longitude) | (52, 5, 717, 1121)  |
| IP5    | papt        | Pseudo-adiabatic potential temperature                                      | (time, 'isobaricInhPa', latitude, longitude) | (52, 20, 717, 1121) |
| IP5    | z           | Geopotential                                                                | (time, 'potentialVorticity', latitude, longitude) | (52, 2, 717, 1121)  |
| IP5    | u           | U component of wind                                                         | (time, 'potentialVorticity', latitude, longitude) | (52, 2, 717, 1121)  |
| IP5    | v           | V component of wind                                                         | (time, 'potentialVorticity', latitude, longitude) | (52, 2, 717, 1121)  |
| HP1    | ws          | Wind speed                                                                  | (time, heightAboveGround, latitude, longitude) | (52, 22, 717, 1121) |
| HP1    | u           | U component of wind                                                         | (time, heightAboveGround, latitude, longitude) | (52, 22, 717, 1121) |
| HP1    | v           | V component of wind                                                         | (time, heightAboveGround, latitude, longitude) | (52, 22, 717, 1121) |
| HP1    | pres        | Pressure                                                                    | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
| HP1    | t           | Temperature                                                                 | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
| HP1    | r           | Relative humidity                                                           | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
| HP1    | u10         | 10 metre U wind component                                                   | (time, latitude, longitude)              | (52, 717, 1121)     |
| HP1    | v10         | 10 metre V wind component                                                   | (time, latitude, longitude)              | (52, 717, 1121)     |
| HP1    | si10        | 10 metre wind speed                                                         | (time, latitude, longitude)              | (52, 717, 1121)     |
| HP1    | wdir10      | 10 metre wind direction                                                     | (time, latitude, longitude)              | (52, 717, 1121)     |
| HP1    | wdir        | Wind direction                                                              | (time, heightAboveGround, latitude, longitude) | (52, 24, 717, 1121) |
| HP1    | u200        | 200 metre U wind component                                                  | (time, latitude, longitude)              | (52, 717, 1121)     |
| HP1    | v200        | 200 metre V wind component                                                  | (time, latitude, longitude)              | (52, 717, 1121)     |
| HP1    | si200       | 200 metre wind speed                                                        | (time, latitude, longitude)              | (52, 717, 1121)     |
| HP1    | u100        | 100 metre U wind component                                                  | (time, latitude, longitude)              | (52, 717, 1121)     |
| HP1    | v100        | 100 metre V wind component                                                  | (time, latitude, longitude)              | (52, 717, 1121)     |
| HP1    | si100       | 100 metre wind speed                                                        | (time, latitude, longitude)              | (52, 717, 1121)     |
| HP2    | crwc        | Specific rain water content                                                 | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
| HP2    | cswc        | Specific snow water content                                                 | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
| HP2    | z           | Geopotential                                                                | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
| HP2    | q           | Specific humidity                                                           | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
| HP2    | clwc        | Specific cloud liquid water content                                         | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
| HP2    | ciwc        | Specific cloud ice water content                                            | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
| HP2    | cc          | Fraction of cloud cover                                                     | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
| HP2    | dpt         | Dew point temperature                                                       | (time, heightAboveGround, latitude, longitude) | (52, 25, 717, 1121) |
| HP2    | tke         | Turbulent kinetic energy                                                    | (time, heightAboveGround, latitude, longitude) | (51, 25, 717, 1121) |
