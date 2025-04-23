from gc import collect

import pytest

from meteofetch import (
    MFWAM0025,
    MFWAM01,
    Arome001,
    Arome0025,
    AromeOutreMerAntilles,
    AromeOutreMerGuyane,
    AromeOutreMerIndien,
    AromeOutreMerNouvelleCaledonie,
    AromeOutreMerPolynesie,
    Arpege01,
    Arpege025,
    Ecmwf,
    set_grib_defs,
    set_test_mode,
)

set_test_mode()

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
    MFWAM0025,
    MFWAM01,
)

# Limiter le nombre de groupes pour tous les modèles
for m in MODELS + (Ecmwf,):
    m.groups_ = m.groups_[:2]

# Liste des configurations GRIB à tester
GRIB_DEFS = ["eccodes", "meteofrance"]


# Fixture pour les modèles
@pytest.fixture(params=MODELS)
def model(request):
    return request.param


# Fixture pour les configurations GRIB
@pytest.fixture(params=GRIB_DEFS)
def grib_def(request):
    return request.param


def test_ecmwf():
    datasets = Ecmwf.get_latest_forecast()
    for field in datasets:
        print(f"\t{field} - {datasets[field].units}")
        ds = datasets[field]
        if "time" in ds.dims:
            assert ds.time.size > 0, f"Le champ {field} n'a pas de données temporelles."
        assert ds.mean() < 1, f"Le champ {field} contient trop de valeurs manquantes."
    del datasets
    collect()


def test_meteo_france_models_with_grib_defs(grib_def, model):
    # Configurer les définitions GRIB
    set_grib_defs(grib_def)
    print(f"\nTesting {model.__name__} with {grib_def} definitions")

    for paquet in model.paquets_:
        print(f"\nModel: {model.__name__}, GRIB defs: {grib_def}, Paquet: {paquet}")
        datasets = model.get_latest_forecast(paquet=paquet)
        assert len(datasets) > 0, f"{paquet} : aucun dataset n'a été récupéré."

        for field in datasets:
            print(f"\t{field} - {datasets[field].units}")
            ds = datasets[field]
            if "time" in ds.dims:
                assert ds.time.size > 0, f"Le champ {field} n'a pas de données temporelles."
            assert ds.mean() < 1, f"Le champ {field} contient trop de valeurs manquantes."
        del datasets
        collect()
