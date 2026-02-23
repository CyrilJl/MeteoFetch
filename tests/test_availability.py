import datetime as dt

import pandas as pd
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
)

pytestmark = pytest.mark.availability

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
ALL_MODELS = METEOFRANCE_MODELS + ECMWF_MODELS

# Keep availability tests network-light while still exercising every model class.
for model in ALL_MODELS:
    model.groups_ = model.groups_[:2]


@pytest.mark.parametrize("model", ECMWF_MODELS)
def test_ecmwf_availability_returns_boolean_series(model):
    availability = model.availability()

    assert isinstance(availability, pd.Series)
    assert availability.name == model.__name__.lower()
    assert len(availability) == model.past_runs_
    assert availability.index.is_monotonic_decreasing
    assert availability.map(lambda value: isinstance(value, bool)).all()


@pytest.mark.parametrize("model", ECMWF_MODELS)
def test_ecmwf_availability_return_date_series(model):
    availability = model.availability(return_date=True)

    assert isinstance(availability, pd.Series)
    assert len(availability) == model.past_runs_
    assert availability.index.is_monotonic_decreasing
    assert availability.map(lambda value: value is False or isinstance(value, dt.datetime)).all()


@pytest.mark.parametrize("grib_def", ("eccodes", "meteofrance"))
@pytest.mark.parametrize("model", METEOFRANCE_MODELS)
def test_meteofrance_availability_returns_boolean_dataframe(model, grib_def):
    set_grib_defs(grib_def)
    availability = model.availability()

    assert isinstance(availability, pd.DataFrame)
    assert list(availability.columns) == list(model.paquets_)
    assert len(availability) == model.past_runs_
    assert availability.index.is_monotonic_decreasing
    assert availability.map(lambda value: isinstance(value, bool)).to_numpy().all()


@pytest.mark.parametrize("model", METEOFRANCE_MODELS)
def test_meteofrance_availability_return_date_dataframe(model):
    availability = model.availability(return_date=True)

    assert isinstance(availability, pd.DataFrame)
    assert list(availability.columns) == list(model.paquets_)
    assert len(availability) == model.past_runs_
    assert availability.index.is_monotonic_decreasing
    assert availability.map(lambda value: value is False or isinstance(value, dt.datetime)).to_numpy().all()
