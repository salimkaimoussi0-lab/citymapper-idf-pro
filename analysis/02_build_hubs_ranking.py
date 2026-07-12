import argparse

from _common import TABLEAUX_DIR, build_stop_line_table, ensure_output_dirs, find_data_file


def main():
    parser = argparse.ArgumentParser(description="Classement des gares par nombre de correspondances.")
    parser.add_argument("--gtfs", default="IDFM-gtfs.zip")
    args = parser.parse_args()

    ensure_output_dirs()
    gtfs_zip = find_data_file(args.gtfs)

    print(f"Lecture GTFS : {gtfs_zip}")
    data = build_stop_line_table(gtfs_zip)

    hubs = (
        data.groupby("stop_name")["route_short_name"]
        .apply(lambda s: sorted(set(x for x in s if str(x).strip())))
        .reset_index()
    )

    hubs["Nombre_Correspondances"] = hubs["route_short_name"].apply(len)
    hubs["Lignes_Desservies"] = hubs["route_short_name"].apply(lambda x: ", ".join(x))

    hubs = hubs.rename(columns={"stop_name": "Nom de la Gare / Station"})
    hubs = hubs[["Nom de la Gare / Station", "Nombre_Correspondances", "Lignes_Desservies"]]
    hubs = hubs.sort_values("Nombre_Correspondances", ascending=False)

    csv_path = TABLEAUX_DIR / "02_classement_correspondances_idf.csv"
    xlsx_path = TABLEAUX_DIR / "02_classement_correspondances_idf.xlsx"

    hubs.to_csv(csv_path, index=False)
    hubs.to_excel(xlsx_path, index=False)

    print(f"OK CSV généré : {csv_path}")
    print(f"OK Excel généré : {xlsx_path}")
    print(hubs.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
