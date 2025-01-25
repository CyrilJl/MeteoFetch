# MeteoFetch

Récupération des prévisions modèles MétéoFrance Arome 0.025° et 0.01° **sans clé d'API**.

# Usage

```python
from meteofetch import Arome0025

datasets = Arome0025.get_latest_forecast(paquet='SP3')
datasets['ssr'].isel(time=5).plot(cmap='Spectral_r')
```
