import pandas as pd

from meteofetch import (
    Arome001,
    Arome0025,
    AromeOutreMerAntilles,
    Arpege01,
    Arpege025,
    Ecmwf,
    set_test_mode,
)

set_test_mode()


def print_rst_table(header, data):
    """
    Prints a list of lists as a reStructuredText grid table.
    """
    # Calculate column widths
    column_widths = [len(h) for h in header]
    for row in data:
        for i, cell in enumerate(row):
            if len(str(cell)) > column_widths[i]:
                column_widths[i] = len(str(cell))

    # Print table header
    header_line = "+" + "+".join(["-" * (w + 2) for w in column_widths]) + "+"
    print(header_line)
    header_row = "| " + " | ".join([h.ljust(w) for h, w in zip(header, column_widths)]) + " |"
    print(header_row)
    print(header_line.replace("-", "="))

    # Print table data
    for row in data:
        data_row = "| " + " | ".join([str(c).ljust(w) for c, w in zip(row, column_widths)]) + " |"
        print(data_row)
        print(header_line)


def generate_tables():
    """
    Generates and prints RST tables for weather models.
    """
    models = [
        Arome001,
        Arome0025,
        AromeOutreMerAntilles,
        Arpege01,
        Arpege025,
    ]

    for model in models:
        print(f"{model.__name__}")
        print("-" * len(model.__name__))

        header = ["Paquet", "Champ", "Description", "Unité", "Dimensions", "Shape dun run complet", "Horizon de prévision"]
        table_data = []

        for paquet in model.paquets_:
            try:
                datasets = model.get_latest_forecast(paquet=paquet, num_workers=6)
                for i, field in enumerate(datasets):
                    ds = datasets[field]
                    paquet_name = paquet if i == 0 else ""
                    row = [
                        paquet_name,
                        field,
                        ds.attrs.get('long_name', 'N/A'),
                        ds.attrs.get('units', 'N/A'),
                        str(tuple(ds.dims)),
                        str(ds.shape),
                        str(pd.to_timedelta(ds['time'].max().item() - ds['time'].min().item())),
                    ]
                    table_data.append(row)
            except Exception as e:
                print(f"Could not fetch data for {model.__name__} - {paquet}: {e}")

        print_rst_table(header, table_data)
        print("\n\n")

    # Special case for Ecmwf
    print("Ecmwf")
    print("-----")
    header_ecmwf = ["Champ", "Description", "Unité", "Dimensions", "Shape dun run complet", "Horizon de prévision"]
    table_data_ecmwf = []
    try:
        datasets = Ecmwf.get_latest_forecast(num_workers=6)
        for field in datasets:
            ds = datasets[field]
            row = [
                field,
                ds.attrs.get('long_name', 'N/A'),
                ds.attrs.get('units', 'N/A'),
                str(tuple(ds.dims)),
                str(ds.shape),
                str(pd.to_timedelta(ds['time'].max().item() - ds['time'].min().item())),
            ]
            table_data_ecmwf.append(row)
        print_rst_table(header_ecmwf, table_data_ecmwf)
    except Exception as e:
        print(f"Could not fetch data for Ecmwf: {e}")


if __name__ == "__main__":
    generate_tables()
