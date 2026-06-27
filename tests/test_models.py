"""
Tests fonctionnels pour les modèles meteofetch.
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

_METEOFRANCE_MODELS = (
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

_ECMWF_MODELS = (Ifs, Aifs)
_ALL_MODELS = _METEOFRANCE_MODELS + _ECMWF_MODELS

# FIX: au lieu de muter les classes originales, on crée des sous-classes
# locales avec groups_ tronqué. Les classes originales restent intactes.
def _make_limited(cls, n_groups: int = 2):
    """Return a subclass of *cls* with groups_ limited to the first *n_groups* entries."""
    return type(
        f"{cls.__name__}Limited",
        (cls,),
        {"groups_": cls.groups_[:n_groups]},
    )


# Variantes limitées pour les tests (2 groupes au lieu de tous)
_LIMITED_MF_MODELS = [_make_limited(m) for m in _METEOFRANCE_MODELS]
_LIMITED_IFS = _make_limited(Ifs)
_LIMITED_AIFS = _make_limited(Aifs)

GRIB_DEFS = ["eccodes", "meteofrance"]


@pytest.fixture(params=_LIMITED_MF_MODELS, ids=[m.__name__ for m in _METEOFRANCE_MODELS])
def mf_model(request):
    return request.param


@pytest.fixture(params=GRIB_DEFS)
def grib_def(request):
    return request.param


def test_aifs():
    datasets = _LIMITED_AIFS.get_latest_forecast()
    for field in datasets:
        print(f"\t{field} - {datasets[field].units}")
        ds = datasets[field]
        if "time" in ds.dims:
            assert ds.time.size > 0, f"Le champ {field} n'a pas de données temporelles."
        assert ds.mean() < 1, f"Le champ {field} contient trop de valeurs manquantes."
    del datasets
    collect()


def test_ifs():
    datasets = _LIMITED_IFS.get_latest_forecast()
    for field in datasets:
        print(f"\t{field} - {datasets[field].units}")
        ds = datasets[field]
        if "time" in ds.dims:
            assert ds.time.size > 0, f"Le champ {field} n'a pas de données temporelles."
        assert ds.mean() < 1, f"Le champ {field} contient trop de valeurs manquantes."
    del datasets
    collect()


def test_meteo_france_models_with_grib_defs(grib_def, mf_model):
    set_grib_defs(grib_def)
    print(f"\nTesting {mf_model.__name__} with {grib_def} definitions")
    print(mf_model.availability())

    for paquet in mf_model.paquets_:
        print(f"\nModel: {mf_model.__name__}, GRIB defs: {grib_def}, Paquet: {paquet}")
        datasets = mf_model.get_latest_forecast(paquet=paquet)
        assert len(datasets) > 0, f"{paquet} : aucun dataset n'a été récupéré."

        for field in datasets:
            print(f"\t{field} - {datasets[field].units}")
            ds = datasets[field]
            if "time" in ds.dims:
                assert ds.time.size > 0, f"Le champ {field} n'a pas de données temporelles."
            assert ds.mean() < 1, f"Le champ {field} contient trop de valeurs manquantes."
        del datasets
        collect()
