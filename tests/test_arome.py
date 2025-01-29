from meteofetch import Arome001, Arome0025, AromeOutreMerIndien, Arpege01, Arpege025


def test_Arome001():
    model = Arome0025()
    datasets = model.get_latest_forecast(paquet="SP1")
    assert len(datasets) > 0
    for field in datasets:
        assert datasets[field].time.size > 0
        assert datasets[field].isnull().mean() < 1


def test_Arome0025():
    model = Arome001()
    datasets = model.get_latest_forecast(paquet="SP1", variables=("u10", "v10"))
    assert len(datasets) > 0
    for field in datasets:
        assert datasets[field].time.size > 0
        assert datasets[field].isnull().mean() < 1


def test_Arpege01():
    model = Arpege01()
    datasets = model.get_latest_forecast(paquet="SP1")
    assert len(datasets) > 0
    for field in datasets:
        assert datasets[field].time.size > 0
        assert datasets[field].isnull().mean() < 1


def test_Arpege025():
    model = Arpege025()
    datasets = model.get_latest_forecast(paquet="SP1", variables=("u10", "v10"))
    assert len(datasets) > 0
    for field in datasets:
        assert datasets[field].time.size > 0
        assert datasets[field].isnull().mean() < 1


def test_AromeOutreMerIndien():
    model = AromeOutreMerIndien()
    datasets = model.get_latest_forecast(paquet="SP1")
    assert len(datasets) > 0
    for field in datasets:
        assert datasets[field].time.size > 0
        assert datasets[field].isnull().mean() < 1
