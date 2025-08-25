import pandas as pd

from meteofetch import (
    Aifs,
    Arome001,
    Arome0025,
    AromeOutreMerAntilles,
    Arpege01,
    Arpege025,
    Ifs,
    set_test_mode,
)

set_test_mode()


def generate_rst_table(header, data):
    """
    Generates a reStructuredText grid table as a string.
    """
    # Calculate column widths
    column_widths = [len(h) for h in header]
    for row in data:
        for i, cell in enumerate(row):
            if len(str(cell)) > column_widths[i]:
                column_widths[i] = len(str(cell))

    # Build table header
    header_line = "+" + "+".join(["-" * (w + 2) for w in column_widths]) + "+"
    header_row = "| " + " | ".join([h.ljust(w) for h, w in zip(header, column_widths)]) + " |"
    separator_line = header_line.replace("-", "=")

    # Build table content
    table_content = [header_line, header_row, separator_line]

    # Add table data
    for row in data:
        data_row = "| " + " | ".join([str(c).ljust(w) for c, w in zip(row, column_widths)]) + " |"
        table_content.append(data_row)
        table_content.append(header_line)

    return "\n".join(table_content)


def generate_tables():
    """
    Generates RST tables for weather models and saves to a file.
    """
    models = [
        Arome001,
        Arome0025,
        AromeOutreMerAntilles,
        Arpege01,
        Arpege025,
    ]

    rst_content = []

    for model in models:
        rst_content.append(f"{model.__name__}")
        rst_content.append("-" * len(model.__name__))
        rst_content.append("")

        header = [
            "Paquet",
            "Champ",
            "Description",
            "Unité",
            "Dimensions",
            "Shape dun run complet",
            "Horizon de prévision",
        ]
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
                        ds.attrs.get("long_name", "N/A"),
                        ds.attrs.get("units", "N/A"),
                        f"({', '.join(ds.dims)})",
                        str(ds.shape),
                        str(pd.to_timedelta(ds["time"].max().item() - ds["time"].min().item())),
                    ]
                    table_data.append(row)
            except Exception as e:
                rst_content.append(f"Could not fetch data for {model.__name__} - {paquet}: {e}")
                rst_content.append("")

        if table_data:
            rst_content.append(generate_rst_table(header, table_data))
        rst_content.append("")
        rst_content.append("")

    # Special case for Ifs
    rst_content.append("Ifs")
    rst_content.append("---")
    rst_content.append("")

    header_ifs = ["Champ", "Description", "Unité", "Dimensions", "Shape dun run complet", "Horizon de prévision"]
    table_data_ifs = []

    try:
        datasets = Ifs.get_latest_forecast(num_workers=6)
        for field in datasets:
            ds = datasets[field]
            row = [
                field,
                ds.attrs.get("long_name", "N/A"),
                ds.attrs.get("units", "N/A"),
                f"({', '.join(ds.dims)})",
                str(ds.shape),
                str(pd.to_timedelta(ds["time"].max().item() - ds["time"].min().item())),
            ]
            table_data_ifs.append(row)

        if table_data_ifs:
            rst_content.append(generate_rst_table(header_ifs, table_data_ifs))
    except Exception as e:
        rst_content.append(f"Could not fetch data for Ifs: {e}")
        rst_content.append("")

    # Special case for Aifs
    rst_content.append("Aifs")
    rst_content.append("----")
    rst_content.append("")

    header_aifs = ["Champ", "Description", "Unité", "Dimensions", "Shape dun run complet", "Horizon de prévision"]
    table_data_aifs = []

    try:
        datasets = Aifs.get_latest_forecast(num_workers=6)
        for field in datasets:
            ds = datasets[field]
            row = [
                field,
                ds.attrs.get("long_name", "N/A"),
                ds.attrs.get("units", "N/A"),
                str(tuple(ds.dims)),
                str(ds.shape),
                str(pd.to_timedelta(ds["time"].max().item() - ds["time"].min().item())),
            ]
            table_data_aifs.append(row)

        if table_data_aifs:
            rst_content.append(generate_rst_table(header_aifs, table_data_aifs))
    except Exception as e:
        rst_content.append(f"Could not fetch data for Aifs: {e}")
        rst_content.append("")

    # Save to file
    with open("weather_models_tables.rst", "w", encoding="utf-8") as f:
        f.write("\n".join(rst_content))

    print("Tables saved to weather_models_tables.rst")


if __name__ == "__main__":
    generate_tables()
