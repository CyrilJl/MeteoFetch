import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely import box

from meteofetch import (
    Arome001,
    Arome0025,
    AromeOutreMerAntilles,
    AromeOutreMerGuyane,
    AromeOutreMerIndien,
    AromeOutreMerNouvelleCaledonie,
    AromeOutreMerPolynesie,
    Arpege01,
    set_test_mode,
)

set_test_mode()

world = gpd.read_file(
    "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/country_shapes/exports/geojson?lang=fr&timezone=Europe%2FBerlin"
)

for model in (
    Arome001,
    Arome0025,
    AromeOutreMerAntilles,
    AromeOutreMerGuyane,
    AromeOutreMerIndien,
    AromeOutreMerNouvelleCaledonie,
    AromeOutreMerPolynesie,
    Arpege01,
):
    model.groups_ = model.groups_[:1]
    datasets = model.get_latest_forecast(paquet="SP1")
    field = list(datasets.keys())[0]
    ds = datasets[field]
    dx = np.diff(ds.longitude)[0]
    dy = np.diff(ds.latitude)[0]
    xmin, xmax = np.min(ds.longitude.values) - dx / 2, np.max(ds.longitude.values) + dx / 2
    ymin, ymax = np.min(ds.latitude.values) - dy / 2, np.max(ds.latitude.values) + dy / 2
    b = box(xmin, ymin, xmax, ymax)
    b = gpd.GeoSeries([b], crs=4326)

    world.clip(b.buffer(6)).plot(figsize=(7, 7), fc="none", lw=0.7)
    b.plot(ax=plt.gca(), fc="C1", ec="none", alpha=0.5)
    plt.gca().axis("off")
    plt.title(model.__name__)
    plt.xlim(xmin - 5, xmax + 5)
    plt.ylim(ymin - 5, ymax + 5)
    plt.tight_layout()
    plt.savefig(f"docs/source/_static/domain_{model.__name__}.png", bbox_inches="tight")
    plt.show()
