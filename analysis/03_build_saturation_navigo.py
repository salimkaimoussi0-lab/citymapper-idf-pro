import argparse

import pandas as pd
import plotly.express as px
from rapidfuzz import process, fuzz

from _common import (
    CARTES_DIR,
    TABLEAUX_DIR,
    build_stop_line_table,
    clean_number_series,
    detect_column,
    ensure_output_dirs,
    find_data_file,
    normalize_text,
)


def main():
    parser = argparse.ArgumentParser(description="Carte de saturation réelle avec validations Navigo.")
    parser.add_argument("--gtfs", default="IDFM-gtfs.zip")
    parser.add_argument("--navigo", default="validations_navigo.csv")
    parser.add_argument("--min-score", type=int, default=86)
    args = parser.parse_args()

    ensure_output_dirs()

    gtfs_zip = find_data_file(args.gtfs)
    navigo_csv = find_data_file(args.navigo)

    print(f"Lecture GTFS : {gtfs_zip}")
    print(f"Lecture Navigo : {navigo_csv}")

    stops_lines = build_stop_line_table(gtfs_zip)

    df_nav = pd.read_csv(navigo_csv, sep=";", low_memory=False)

    station_col = detect_column(
        df_nav,
        ["LIBELLE_ARRET", "NOM_ARRET", "ARRET", "STOP_NAME", "GARE", "STATION"],
    )
    validations_col = detect_column(
        df_nav,
        ["NB_VALD", "VALIDATIONS", "NB_VALIDATIONS", "VOYAGEURS"],
    )

    df_nav = df_nav[[station_col, validations_col]].copy()
    df_nav.columns = ["navigo_station", "NB_VALD"]
    df_nav["NB_VALD"] = clean_number_series(df_nav["NB_VALD"])
    df_nav = df_nav.dropna(subset=["navigo_station", "NB_VALD"])

    nav_stats = (
        df_nav.groupby("navigo_station", as_index=False)["NB_VALD"]
        .mean()
        .sort_values("NB_VALD", ascending=False)
    )

    nav_stats["navigo_norm"] = nav_stats["navigo_station"].apply(normalize_text)

    unique_nav = nav_stats["navigo_norm"].dropna().unique().tolist()
    nav_by_norm = nav_stats.set_index("navigo_norm")

    station_names = sorted(stops_lines["stop_name"].dropna().unique())

    matches = []

    print("Matching GTFS ↔ Navigo en cours...")
    for name in station_names:
        norm = normalize_text(name)

        if not norm:
            continue

        match = process.extractOne(norm, unique_nav, scorer=fuzz.WRatio)

        if not match:
            continue

        matched_norm, score, _ = match

        if score >= args.min_score:
            row = nav_by_norm.loc[matched_norm]

            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]

            matches.append(
                {
                    "stop_name": name,
                    "match_navigo": row["navigo_station"],
                    "score_match": score,
                    "NB_VALD": row["NB_VALD"],
                }
            )

    matched_df = pd.DataFrame(matches)

    result = stops_lines.merge(matched_df, on="stop_name", how="inner")

    csv_path = TABLEAUX_DIR / "03_saturation_navigo_stations.csv"
    result.to_csv(csv_path, index=False)

    color_map = dict(zip(result["route_short_name"], result["route_color"]))

    fig = px.scatter_mapbox(
        result,
        lat="stop_lat",
        lon="stop_lon",
        hover_name="stop_name",
        hover_data={
            "match_navigo": True,
            "NB_VALD": ":.0f",
            "route_short_name": True,
            "score_match": True,
            "stop_lat": False,
            "stop_lon": False,
        },
        color="route_short_name",
        color_discrete_map=color_map,
        size="NB_VALD",
        size_max=28,
        zoom=10,
        height=850,
        title="Saturation réelle du réseau IDF - Validations Navigo",
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        legend_title_text="Lignes RATP/SNCF",
    )

    html_path = CARTES_DIR / "03_saturation_navigo_idf.html"
    fig.write_html(html_path)

    print(f"OK tableau généré : {csv_path}")
    print(f"OK carte générée : {html_path}")
    print(f"Stations matchées : {len(matched_df)}")


if __name__ == "__main__":
    main()
