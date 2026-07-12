import argparse

import plotly.express as px

from _common import (
    CARTES_DIR,
    TABLEAUX_DIR,
    build_stop_line_table,
    ensure_output_dirs,
    find_data_file,
)


def main():
    parser = argparse.ArgumentParser(description="Carte interactive du réseau ferré IDF.")
    parser.add_argument("--gtfs", default="IDFM-gtfs.zip")
    args = parser.parse_args()

    ensure_output_dirs()
    gtfs_zip = find_data_file(args.gtfs)

    print(f"Lecture GTFS : {gtfs_zip}")
    stops_final = build_stop_line_table(gtfs_zip)

    stops_final.to_csv(TABLEAUX_DIR / "01_reseau_stations_lignes.csv", index=False)

    color_map = dict(
        zip(stops_final["route_short_name"], stops_final["route_color"])
    )

    fig = px.scatter_mapbox(
        stops_final,
        lat="stop_lat",
        lon="stop_lon",
        hover_name="stop_name",
        hover_data={
            "route_short_name": True,
            "stop_lat": False,
            "stop_lon": False,
        },
        color="route_short_name",
        color_discrete_map=color_map,
        zoom=9,
        height=800,
        title="Réseau interactif RATP / SNCF - Île-de-France",
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        legend_title_text="Lignes RATP/SNCF",
    )

    output = CARTES_DIR / "01_reseau_interactif_idf.html"
    fig.write_html(output)

    print(f"OK carte générée : {output}")
    print(f"OK tableau généré : {TABLEAUX_DIR / '01_reseau_stations_lignes.csv'}")


if __name__ == "__main__":
    main()
