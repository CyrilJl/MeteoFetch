import logging
import os

import xarray as xr

from meteofetch._misc import geo_encode_cf, set_test_mode


def test_geo_encode_cf_does_not_mutate_source_dataarray():
    da = xr.DataArray([1, 2], dims="time", coords={"time": [0, 1]})

    encoded = geo_encode_cf(da)

    assert encoded is not da
    assert encoded.data is da.data
    assert da.encoding == {}
    assert "spatial_ref" not in da.coords
    assert da["time"].encoding == {}
    assert encoded.encoding["zlib"] is True
    assert "spatial_ref" in encoded.coords


def test_set_test_mode_logs_message(caplog, monkeypatch):
    monkeypatch.setenv("METEOFETCH_TEST_MODE", "0")

    with caplog.at_level(logging.INFO, logger="meteofetch._misc"):
        set_test_mode()

    assert os.environ["METEOFETCH_TEST_MODE"] == "1"
    assert "Test mode enabled" in caplog.text
