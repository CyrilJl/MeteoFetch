import sys
from types import SimpleNamespace

from meteofetch import _model
from meteofetch._model import Model


class FakeEccodes:
    def __init__(self, messages):
        self.messages = list(messages)
        self.released = []

    def codes_grib_new_from_file(self, source):
        return self.messages.pop(0) if self.messages else None

    def codes_get(self, message, key):
        assert key == "shortName"
        return message.short_name

    def codes_write(self, message, target):
        target.write(message.payload)

    def codes_release(self, message):
        self.released.append(message)


def test_split_grib_by_short_name_groups_messages(monkeypatch, tmp_path):
    messages = [
        SimpleNamespace(short_name="2t", payload=b"temperature-0"),
        SimpleNamespace(short_name="10u", payload=b"wind"),
        SimpleNamespace(short_name="2t", payload=b"temperature-1"),
    ]
    fake_eccodes = FakeEccodes(messages)
    monkeypatch.setitem(sys.modules, "eccodes", fake_eccodes)

    path = tmp_path / "forecast.grib2"
    path.write_bytes(b"source")

    split_paths = Model._split_grib_by_short_name(path, "forecast")

    assert split_paths == [
        tmp_path / "split_forecast_2t.grib2",
        tmp_path / "split_forecast_10u.grib2",
    ]
    assert split_paths[0].read_bytes() == b"temperature-0temperature-1"
    assert split_paths[1].read_bytes() == b"wind"
    assert fake_eccodes.released == messages


def test_large_windows_grib_uses_python_splitter(monkeypatch, tmp_path):
    original_path = tmp_path / "forecast.grib2"
    original_path.write_bytes(b"source")
    split_paths = [tmp_path / "split_forecast_2t.grib2", tmp_path / "split_forecast_10u.grib2"]
    for split_path in split_paths:
        split_path.write_bytes(b"split")

    monkeypatch.setattr(_model, "system", lambda: "Windows")
    monkeypatch.setattr(_model, "getsize", lambda path: 2**31)
    monkeypatch.setattr(Model, "_split_grib_by_short_name", staticmethod(lambda path, file_name: split_paths))

    opened_paths = []

    def fake_open_dataset(path, **kwargs):
        opened_paths.append(path)
        return path.name

    monkeypatch.setattr(_model, "_import_cfgrib", lambda: SimpleNamespace(open_dataset=fake_open_dataset))

    datasets = Model._read_grib(original_path)

    assert datasets == ["split_forecast_2t.grib2", "split_forecast_10u.grib2"]
    assert opened_paths == split_paths
    assert not original_path.exists()
