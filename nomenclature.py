import pandas as pd
from meteofetch import Arome001, Arome0025, AromeOutreMerAntilles, Arpege01, Arpege025, Ecmwf, set_test_mode

set_test_mode()

for model in (
    Arome001,
    Arome0025,
    AromeOutreMerAntilles,
    Arpege01,
    Arpege025,
):
    print(model.__name__)
    print()
    for j, paquet in enumerate(model.paquets_):
        if j == 0:
            print(" Paquet | Champ | Description | Dimensions | Shape dun run complet | Horizon de prévision |")
            print("----------|----------|----------|----------|----------|")
        datasets = model.get_latest_forecast(paquet=paquet, num_workers=6)
        for k, field in enumerate(datasets):
            ds = datasets[field]
            p = " " if k else paquet
            print(
                f"| {p} | {field} | {ds.attrs['long_name']} | {tuple(ds.dims)} | {ds.shape} | {pd.to_timedelta(ds['time'].max().item() - ds['time'].min().item())} |"
            )
    print("\n\n\n")

model = Ecmwf
print(" Champ | Description | Dimensions | Shape dun run complet | Horizon de prévision |")
print("--------|----------|----------|----------|----------|")
datasets = model.get_latest_forecast(num_workers=6)
for k, field in enumerate(datasets):
    ds = datasets[field]
    print(
        f"| {field} | {ds.attrs['long_name']} | {tuple(ds.dims)} | {ds.shape} | {pd.to_timedelta(ds['time'].max().item() - ds['time'].min().item())} |"
    )
