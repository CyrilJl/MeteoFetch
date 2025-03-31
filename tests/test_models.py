from gc import collect

import pytest
# Imports a priori non-utiles pour checker
# si les librairies sont bien rechargées
# et ECCODES_DEFINITION_PATH est bien prise
# en compte
import xarray as xr
import cfgrib

from meteofetch import (
    Arome001,
    Arome0025,
    AromeOutreMerAntilles,
    AromeOutreMerGuyane,
    AromeOutreMerIndien,
    AromeOutreMerNouvelleCaledonie,
    AromeOutreMerPolynesie,
    Arpege01,
    Arpege025,
)

MODELS = (
    Arome001,
    Arome0025,
    AromeOutreMerAntilles,
    AromeOutreMerGuyane,
    AromeOutreMerIndien,
    AromeOutreMerNouvelleCaledonie,
    AromeOutreMerPolynesie,
    Arpege01,
    Arpege025,
)

# Limiter le nombre de groupes pour tous les modèles
for m in MODELS:
    m.groups_ = m.groups_[:2]


# Fixture unique pour tous les modèles
@pytest.fixture(params=MODELS)
def model(request):
    return request.param()


# Test unique pour tous les modèles
def test_models(model):
    for paquet in model.paquets_:
        print(f"\nModel: {model.__class__.__name__}, Paquet: {paquet}")
        datasets = model.get_latest_forecast(paquet=paquet)
        assert len(datasets) > 0, f"{paquet} : aucun dataset n'a été récupéré."

        for field in datasets:
            print(f"\t{field}")
            ds = datasets[field]
            if "time" in ds.dims:
                assert ds.time.size > 0, f"Le champ {field} n'a pas de données temporelles."
            assert ds.isnull().mean() < 1, f"Le champ {field} contient trop de valeurs manquantes."
        del datasets
        collect()
