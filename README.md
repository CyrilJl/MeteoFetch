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

| **Paquet** | **Champs**                                                                 | **Description**                                                                 |
|------------|----------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| **SP1**    | `u10`                                                                     | 10 metre U wind component                                                       |
|            | `v10`                                                                     | 10 metre V wind component                                                       |
|            | `t2m`                                                                     | 2 metre temperature                                                             |
|            | `r2`                                                                      | 2 metre relative humidity                                                       |
|            | `efg10`                                                                   | 10 metre eastward wind gust since previous post-processing                      |
|            | `nfg10`                                                                   | 10 metre northward wind gust since previous post-processing                     |
| **SP2**    | `sp`                                                                      | Surface pressure                                                                |
|            | `CAPE_INS`                                                                | Convective Available Potential Energy instantaneous                             |
|            | `lcc`                                                                     | Low cloud cover                                                                 |
|            | `mcc`                                                                     | Medium cloud cover                                                              |
|            | `hcc`                                                                     | High cloud cover                                                                |
|            | `tgrp`                                                                    | Graupel (snow pellets) precipitation                                            |
|            | `tirf`                                                                    | Time integral of rain flux                                                      |
|            | `tsnowp`                                                                  | Total snow precipitation                                                        |
| **SP3**    | `h`                                                                       | Geometrical height                                                              |
| **HP1**    | `ws`                                                                      | Wind speed                                                                      |
|            | `u`                                                                       | U component of wind                                                             |
|            | `v`                                                                       | V component of wind                                                             |
|            | `r`                                                                       | Relative humidity                                                               |
|            | `u10`                                                                     | 10 metre U wind component                                                       |
|            | `v10`                                                                     | 10 metre V wind component                                                       |
|            | `si10`                                                                    | 10 metre wind speed                                                             |
|            | `wdir10`                                                                  | 10 metre wind direction                                                         |
|            | `wdir`                                                                    | Wind direction                                                                  |
|            | `u100`                                                                    | 100 metre U wind component                                                      |
|            | `v100`                                                                    | 100 metre V wind component                                                      |
|            | `si100`                                                                   | 100 metre wind speed                                                            |
