"""Tests fonctionnels (smoke tests) des modèles meteofetch.

En mode test (``set_test_mode()``), les valeurs téléchargées sont remplacées par
leur masque ``isnull()`` (1 = valeur manquante). Ces tests vérifient donc que le
pipeline *téléchargement → lecture GRIB → mise en forme* fonctionne et renvoie
des données correctement structurées, sans dépendre du contenu météo réel.

Pour rester rapides (le job CI téléchargeait auparavant l'ensemble des paquets de
tous les modèles, soit >40 min) :

* seules les deux premières échéances (``groups_``) de chaque modèle sont
  téléchargées, via ``monkeypatch`` (aucune mutation permanente des classes) ;
* un seul paquet représentatif est testé par modèle Météo-France.
"""

from gc import collect

import pytest

from meteofetch import (
    MFWAM0025,
    MFWAM01,
    Aifs,
    Arome001,
    Arome0025,
    AromeOutreMerAntilles,
    AromeOutreMerGuyane,
    AromeOutreMerIndien,
    AromeOutreMerNouvelleCaledonie,
    AromeOutreMerPolynesie,
    Arpege01,
    Arpege025,
    Ifs,
    set_grib_defs,
    set_test_mode,
)

set_test_mode()

METEOFRANCE_MODELS = (
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
ECMWF_MODELS = (Ifs, Aifs)

# Nombre d'échéances téléchargées par modèle (garde les tests rapides).
N_GROUPS = 2

# Configurations de définitions GRIB à tester.
GRIB_DEFS = ["eccodes", "meteofrance"]


def _limit_groups(monkeypatch, model):
    """Limite temporairement *model* aux ``N_GROUPS`` premières échéances.

    On modifie l'attribut de la classe *réelle* (donc picklable par le
    ``multiprocessing.Pool`` utilisé pour lire les GRIBs) et ``monkeypatch``
    restaure la valeur d'origine à la fin du test.
    """
    monkeypatch.setattr(model, "groups_", model.groups_[:N_GROUPS])
    return model


def _check_datasets(datasets, context):
    """Vérifie qu'un dictionnaire de DataArrays est structurellement sain.

    En mode test, chaque champ vaut son masque ``isnull()`` : ``mean() < 1``
    signifie « le champ contient au moins une valeur réelle ». Certains champs
    sont légitimement masqués à 100 % sur les échéances échantillonnées (ex.
    humidité du sol, variables océaniques) ; on n'exige donc pas que *chaque*
    champ contienne des données, mais qu'au moins un le fasse — ce qui suffit à
    détecter un pipeline cassé (téléchargement/lecture vide).
    """
    assert len(datasets) > 0, f"{context} : aucun dataset n'a été récupéré."

    has_real_data = False
    for field in datasets:
        ds = datasets[field]
        print(f"\t{field} - {ds.units}")
        if "time" in ds.dims:
            assert ds.time.size > 0, f"{context} : le champ {field} n'a pas de données temporelles."
        if float(ds.mean()) < 1:
            has_real_data = True
    assert has_real_data, f"{context} : tous les champs sont entièrement manquants."


@pytest.fixture(params=ECMWF_MODELS, ids=[m.__name__ for m in ECMWF_MODELS])
def ecmwf_model(request, monkeypatch):
    return _limit_groups(monkeypatch, request.param)


@pytest.fixture(params=METEOFRANCE_MODELS, ids=[m.__name__ for m in METEOFRANCE_MODELS])
def mf_model(request, monkeypatch):
    return _limit_groups(monkeypatch, request.param)


@pytest.fixture(params=GRIB_DEFS)
def grib_def(request):
    return request.param


def test_ecmwf_models(ecmwf_model):
    print(f"\nTesting {ecmwf_model.__name__}")
    datasets = ecmwf_model.get_latest_forecast()
    _check_datasets(datasets, ecmwf_model.__name__)
    del datasets
    collect()


def test_meteo_france_models_with_grib_defs(grib_def, mf_model):
    set_grib_defs(grib_def)
    # Un seul paquet représentatif suffit à valider le pipeline sans télécharger
    # tous les paquets de chaque modèle.
    paquet = mf_model.paquets_[0]
    print(f"\nTesting {mf_model.__name__} with {grib_def} definitions, paquet {paquet}")

    datasets = mf_model.get_latest_forecast(paquet=paquet)
    _check_datasets(datasets, f"{mf_model.__name__}/{grib_def}/{paquet}")
    del datasets
    collect()
