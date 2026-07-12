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
    parser = argparse.ArgumentParser(description="Pouls horaire du réseau IDF.")
    parser.add_argument("--gtfs", default="IDFM-gtfs.zip")
    args = parser.parse_args()

    ensure_output_dirs()
    gtfs_zip = find_data_file(args.gtfs)

    print(f"Lecture GTFS : {gtfs_zip}")

    routes = read_gtfs_table(gtfs_zip, "routes.txt")
    trips = read_gtfs_table(gtfs_zip, "trips.txt", usecols=["route_id", "trip_id"])
    stop_times = read_gtfs_table(gtfs_zip, "stop_times.txt", usecols=["trip_id", "arrival_time"])

    routes["route_id"] = routes["route_id"].astype(str)
    trips["route_id"] = trips["route_id"].astype(str)
    trips["trip_id"] = trips["trip_id"].astype(str)
    stop_times["trip_id"] = stop_times["trip_id"].astype(str)

    routes = filter_ferrous_routes(routes)
    routes["route_color"] = routes.get("route_color", "").apply(clean_route_color)

    trips_routes = trips.merge(
        routes[["route_id", "route_short_name", "route_color"]],
        on="route_id",
        how="inner",
    )

    data = stop_times.merge(trips_routes, on="trip_id", how="inner")
    data = data.dropna(subset=["arrival_time"])

    data["HEURE_BRUTE"] = data["arrival_time"].astype(str).str.split(":").str[0]
    data["HEURE_BRUTE"] = pd.to_numeric(data["HEURE_BRUTE"], errors="coerce")
    data = data.dropna(subset=["HEURE_BRUTE"])
    data["HEURE"] = data["HEURE_BRUTE"].astype(int) % 24

    hourly = (
        data.groupby(["HEURE", "route_short_name"], as_index=False)["trip_id"]
        .count()
        .rename(columns={"trip_id": "NOMBRE_PASSAGES"})
        .sort_values(["HEURE", "route_short_name"])
    )

    csv_path = TABLEAUX_DIR / "05_pouls_horaire_reseau_idf.csv"
    hourly.to_csv(csv_path, index=False)

    fig = px.line(
        hourly,
        x="HEURE",
        y="NOMBRE_PASSAGES",
        color="route_short_name",
        markers=True,
        title="Pouls horaire du réseau IDF - passages par heure et par ligne",
        labels={
            "HEURE": "Heure",
            "NOMBRE_PASSAGES": "Nombre de passages",
            "route_short_name": "Ligne",
        },
    )

    fig.update_layout(
        height=750,
        margin={"r": 20, "t": 60, "l": 40, "b": 40},
    )

    html_path = CARTES_DIR / "05_pouls_horaire_reseau_idf.html"
    fig.write_html(html_path)

    print(f"OK CSV généré : {csv_path}")
    print(f"OK graphique généré : {html_path}")


if __name__ == "__main__":
    main()
