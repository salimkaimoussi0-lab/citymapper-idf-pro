import argparse

import pandas as pd
import plotly.express as px

from _common import (
    CARTES_DIR,
    TABLEAUX_DIR,
    clean_route_color,
    ensure_output_dirs,
    filter_ferrous_routes,
    find_data_file,
    read_gtfs_table,
)


def main():
    parser = argparse.ArgumentParser(description="Indice de tension : validations Navigo / trains.")
    parser.add_argument("--gtfs", default="IDFM-gtfs.zip")
    parser.add_argument(
        "--saturation",
        default=str(TABLEAUX_DIR / "03_saturation_navigo_stations.csv"),
    )
    args = parser.parse_args()

    ensure_output_dirs()

    gtfs_zip = find_data_file(args.gtfs)
    saturation_path = Path(args.saturation) if "Path" in globals() else None

    saturation_file = TABLEAUX_DIR / "03_saturation_navigo_stations.csv"

    if not saturation_file.exists():
        raise FileNotFoundError(
            "Le fichier de saturation est absent.\n"
            "Lance d'abord : python analysis/03_build_saturation_navigo.py"
        )

    print(f"Lecture GTFS : {gtfs_zip}")
    print(f"Lecture saturation : {saturation_file}")

    routes = read_gtfs_table(gtfs_zip, "routes.txt")
    trips = read_gtfs_table(gtfs_zip, "trips.txt", usecols=["route_id", "trip_id"])
    stop_times = read_gtfs_table(gtfs_zip, "stop_times.txt", usecols=["trip_id", "stop_id"])
    stops = read_gtfs_table(gtfs_zip, "stops.txt")

    routes["route_id"] = routes["route_id"].astype(str)
    trips["route_id"] = trips["route_id"].astype(str)
    trips["trip_id"] = trips["trip_id"].astype(str)
    stop_times["trip_id"] = stop_times["trip_id"].astype(str)
    stop_times["stop_id"] = stop_times["stop_id"].astype(str)
    stops["stop_id"] = stops["stop_id"].astype(str)

    routes = filter_ferrous_routes(routes)
    routes["route_color"] = routes.get("route_color", "").apply(clean_route_color)

    trips_routes = trips.merge(
        routes[["route_id", "route_short_name", "route_color"]],
        on="route_id",
        how="inner",
    )

    stop_train_counts = (
        stop_times.merge(trips_routes, on="trip_id", how="inner")
        .merge(stops[["stop_id", "stop_name"]], on="stop_id", how="inner")
        .groupby(["stop_name", "route_short_name"], as_index=False)["trip_id"]
        .nunique()
        .rename(columns={"trip_id": "NB_TRAINS"})
    )

    saturation = pd.read_csv(saturation_file)

    tension = saturation.merge(
        stop_train_counts,
        on=["stop_name", "route_short_name"],
        how="left",
    )

    tension["NB_TRAINS"] = pd.to_numeric(tension["NB_TRAINS"], errors="coerce").fillna(0)
    tension = tension[tension["NB_TRAINS"] > 0].copy()
    tension["INDICE_TENSION"] = tension["NB_VALD"] / tension["NB_TRAINS"]

    tension = tension.sort_values("INDICE_TENSION", ascending=False)

    csv_path = TABLEAUX_DIR / "04_indice_tension_idf.csv"
    xlsx_path = TABLEAUX_DIR / "04_indice_tension_idf.xlsx"

    tension.to_csv(csv_path, index=False)
    tension.to_excel(xlsx_path, index=False)

    color_map = dict(zip(tension["route_short_name"], tension["route_color"]))

    fig = px.scatter_mapbox(
        tension,
        lat="stop_lat",
        lon="stop_lon",
        hover_name="stop_name",
        hover_data={
            "route_short_name": True,
            "NB_VALD": ":.0f",
            "NB_TRAINS": ":.0f",
            "INDICE_TENSION": ":.2f",
            "stop_lat": False,
            "stop_lon": False,
        },
        color="INDICE_TENSION",
        size="NB_VALD",
        size_max=30,
        zoom=10,
        height=850,
        title="Heatmap de tension - Voyageurs par train",
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="Voyageurs<br>par train"),
    )

    html_path = CARTES_DIR / "04_indice_tension_idf.html"
    fig.write_html(html_path)

    print(f"OK CSV généré : {csv_path}")
    print(f"OK Excel généré : {xlsx_path}")
    print(f"OK carte générée : {html_path}")
    print(tension[["stop_name", "route_short_name", "NB_VALD", "NB_TRAINS", "INDICE_TENSION"]].head(20).to_string(index=False))


if __name__ == "__main__":
    from pathlib import Path
    main()
