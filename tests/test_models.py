import pytest

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


# Fixture pour les modèles AROME
@pytest.fixture(params=[Arome001, Arome0025])
def arome_model(request):
    return request.param()


# Fixture pour les modèles ARPEGE
@pytest.fixture(params=[Arpege01, Arpege025])
def arpege_model(request):
    return request.param()


# Fixture pour les modèles AROME Outre-Mer
@pytest.fixture(
    params=[
        AromeOutreMerAntilles,
        AromeOutreMerGuyane,
        AromeOutreMerIndien,
        AromeOutreMerNouvelleCaledonie,
        AromeOutreMerPolynesie,
    ]
)
def arome_outre_mer_model(request):
    return request.param()


# Test pour les modèles AROME
def test_arome_models(arome_model):
    for paquet in ("SP1", "SP2", "HP1"):
        datasets = arome_model.get_latest_forecast(paquet=paquet, variables=("u10", "v10"))
        assert len(datasets) > 0, "Aucun dataset n'a été récupéré."
        for field in datasets:
            print(field)
            assert datasets[field].time.size > 0, f"Le champ {field} n'a pas de données temporelles."
            assert datasets[field].isnull().mean() < 1, f"Le champ {field} contient trop de valeurs manquantes."
        print()


# Test pour les modèles ARPEGE
def test_arpege_models(arpege_model):
    for paquet in ("SP1", "SP2"):
        datasets = arpege_model.get_latest_forecast(paquet=paquet)
        assert len(datasets) > 0, "Aucun dataset n'a été récupéré."
        for field in datasets:
            print(field)
            assert datasets[field].time.size > 0, f"Le champ {field} n'a pas de données temporelles."
            assert datasets[field].isnull().mean() < 1, f"Le champ {field} contient trop de valeurs manquantes."
        print()


# Test pour les modèles AROME Outre-Mer
def test_arome_outre_mer_models(arome_outre_mer_model):
    for paquet in ("SP1", "SP2"):
        datasets = arome_outre_mer_model.get_latest_forecast(paquet=paquet)
        assert len(datasets) > 0, "Aucun dataset n'a été récupéré."
        for field in datasets:
            print(field)
            assert datasets[field].time.size > 0, f"Le champ {field} n'a pas de données temporelles."
            assert datasets[field].isnull().mean() < 1, f"Le champ {field} contient trop de valeurs manquantes."
        print()
