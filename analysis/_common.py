from pathlib import Path
import os
import zipfile
import webbrowser
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"
CARTES = REPORTS / "cartes"
TABLEAUX = REPORTS / "tableaux"
HTML_TABLES = REPORTS / "html_tables"

for d in [DATA_RAW, REPORTS, CARTES, TABLEAUX, HTML_TABLES]:
    d.mkdir(parents=True, exist_ok=True)


def find_file(names):
    search_dirs = [
        DATA_RAW,
        ROOT / "data",
        ROOT,
        Path.cwd(),
        Path.home() / "Downloads",
        Path("/content/drive/MyDrive/Projet_Transports_IDF"),
    ]

    for folder in search_dirs:
        for name in names:
            candidate = folder / name
            if candidate.exists():
                return candidate

    print("Fichier introuvable. Place les fichiers ici :")
    print("data/raw/IDFM-gtfs.zip")
    print("data/raw/validations_navigo.csv")
    raise FileNotFoundError(names[0])


def gtfs_zip_path():
    return find_file(["IDFM-gtfs.zip", "IDFM-gtfs"])


def navigo_csv_path():
    return find_file(["validations_navigo.csv", "validations_navigo"])


def read_gtfs(table_name, usecols=None):
    zip_path = gtfs_zip_path()
    print("Lecture GTFS :", zip_path)
    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open(table_name) as f:
            return pd.read_csv(f, usecols=usecols, low_memory=False)


def clean_route_colors(df):
    df = df.copy()
    if "route_color" not in df.columns:
        df["route_color"] = "666666"

    colors = (
        df["route_color"]
        .fillna("666666")
        .astype(str)
        .str.replace("#", "", regex=False)
        .str.strip()
    )

    colors = colors.where(colors.str.len() >= 6, "666666")
    df["route_color"] = "#" + colors.str[:6]
    return df


def open_file(path):
    if os.environ.get("OPEN_REPORT", "1") == "1":
        webbrowser.open(Path(path).resolve().as_uri())


def save_fig(fig, filename):
    out = CARTES / filename
    fig.write_html(out, include_plotlyjs="cdn", full_html=True)
    print("Carte dynamique générée :", out)
    open_file(out)
    return out


def save_table(df, basename, title=None, max_rows=2000):
    csv_path = TABLEAUX / f"{basename}.csv"
    xlsx_path = TABLEAUX / f"{basename}.xlsx"
    html_path = HTML_TABLES / f"{basename}.html"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_path, index=False)

    preview = df.head(max_rows).copy()
    table_html = preview.to_html(index=False, border=0, classes="data-table")

    html_doc = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>{title or basename}</title>
<style>
body {{
  margin: 0;
  font-family: Arial, sans-serif;
  background: #f4f7fb;
  color: #111827;
}}
header {{
  background: white;
  padding: 24px 32px;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 10;
}}
h1 {{
  margin: 0;
  font-size: 28px;
}}
main {{
  padding: 24px 32px;
}}
.search {{
  width: 100%;
  padding: 14px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  margin-bottom: 16px;
  font-size: 16px;
}}
.table-wrap {{
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  overflow: auto;
  max-height: 760px;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}}
th {{
  position: sticky;
  top: 0;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  padding: 10px;
  text-align: left;
  z-index: 2;
}}
td {{
  border-bottom: 1px solid #eef2f7;
  padding: 9px 10px;
  white-space: nowrap;
}}
tr:hover {{
  background: #f8fafc;
}}
.info {{
  color: #64748b;
  margin: 8px 0 18px 0;
}}
</style>
</head>
<body>
<header>
  <h1>{title or basename}</h1>
  <div class="info">Tableau interactif filtrable — aperçu des {len(preview)} premières lignes sur {len(df)}.</div>
</header>
<main>
  <input class="search" placeholder="Rechercher dans le tableau..." onkeyup="filterTable(this.value)">
  <div class="table-wrap">
    {table_html}
  </div>
</main>
<script>
function filterTable(q) {{
  q = q.toLowerCase();
  document.querySelectorAll("tbody tr").forEach(row => {{
    row.style.display = row.innerText.toLowerCase().includes(q) ? "" : "none";
  }});
}}
</script>
</body>
</html>
"""
    html_path.write_text(html_doc, encoding="utf-8")

    print("Tableau CSV généré :", csv_path)
    print("Tableau Excel généré :", xlsx_path)
    print("Tableau interactif généré :", html_path)

    open_file(html_path)
    return csv_path, xlsx_path, html_path


def build_rail_network():
    print("Extraction GTFS du réseau ferré...")

    routes = read_gtfs("routes.txt")
    trips = read_gtfs("trips.txt", usecols=["route_id", "trip_id"])
    stop_times = read_gtfs("stop_times.txt", usecols=["trip_id", "stop_id"])
    stops = read_gtfs("stops.txt")

    routes["route_id"] = routes["route_id"].astype(str)
    trips["route_id"] = trips["route_id"].astype(str)
    trips["trip_id"] = trips["trip_id"].astype(str)
    stop_times["trip_id"] = stop_times["trip_id"].astype(str)
    stop_times["stop_id"] = stop_times["stop_id"].astype(str)
    stops["stop_id"] = stops["stop_id"].astype(str)

    codes_ferres = [1, 2, 100, 109, 400]
    routes_ferrees = routes[routes["route_type"].isin(codes_ferres)].copy()
    routes_ferrees = clean_route_colors(routes_ferrees)

    trips_colors = pd.merge(
        trips,
        routes_ferrees[["route_id", "route_short_name", "route_color"]],
        on="route_id",
        how="inner",
    )

    stop_to_route = pd.merge(stop_times, trips_colors, on="trip_id", how="inner")
    stop_colors = stop_to_route.drop_duplicates(subset=["stop_id"])

    stops_final = pd.merge(
        stops,
        stop_colors[["stop_id", "route_short_name", "route_color"]],
        on="stop_id",
        how="inner",
    )

    stops_final = stops_final.dropna(subset=["stop_lat", "stop_lon"])
    stops_final = stops_final.sort_values(by="route_short_name")

    color_map = dict(zip(stops_final["route_short_name"], stops_final["route_color"]))

    return routes, trips, stop_times, stops, routes_ferrees, stop_to_route, stops_final, color_map


def build_saturation_dataset():
    from rapidfuzz import process, utils

    print("Chargement des données Navigo...")
    df_navigo = pd.read_csv(navigo_csv_path(), sep=";", low_memory=False)
    df_navigo["NB_VALD"] = pd.to_numeric(df_navigo["NB_VALD"], errors="coerce").fillna(0)

    navigo_stats = (
        df_navigo
        .groupby("LIBELLE_ARRET")["NB_VALD"]
        .mean()
        .reset_index()
    )

    print("Données Navigo chargées avec succès.")

    routes, trips, stop_times, stops, routes_ferrees, stop_to_route, stops_final, color_map = build_rail_network()

    liste_noms_navigo = navigo_stats["LIBELLE_ARRET"].dropna().unique().tolist()

    def trouver_nom_navigo(nom_gtfs):
        resultat = process.extractOne(
            nom_gtfs,
            liste_noms_navigo,
            processor=utils.default_process,
        )
        if resultat and resultat[1] >= 80:
            return resultat[0]
        return None

    print("Calcul des correspondances entre GTFS et Navigo...")
    stops_final = stops_final.copy()
    stops_final["nom_match_navigo"] = stops_final["stop_name"].apply(trouver_nom_navigo)

    stops_complet = pd.merge(
        stops_final,
        navigo_stats,
        left_on="nom_match_navigo",
        right_on="LIBELLE_ARRET",
        how="left",
    )

    stops_complet["NB_VALD"] = stops_complet["NB_VALD"].fillna(0)

    return stops_complet, routes, trips, stop_times, stops, routes_ferrees, stop_to_route, color_map


def load_temporal_data():
    print("Rechargement des données temporelles avec arrival_time...")

    routes = read_gtfs("routes.txt")
    trips = read_gtfs("trips.txt", usecols=["route_id", "trip_id"])
    stop_times = read_gtfs("stop_times.txt", usecols=["trip_id", "stop_id", "arrival_time"])
    stops = read_gtfs("stops.txt")

    routes["route_id"] = routes["route_id"].astype(str)
    trips["route_id"] = trips["route_id"].astype(str)
    trips["trip_id"] = trips["trip_id"].astype(str)
    stop_times["trip_id"] = stop_times["trip_id"].astype(str)
    stop_times["stop_id"] = stop_times["stop_id"].astype(str)
    stops["stop_id"] = stops["stop_id"].astype(str)

    routes_ferrees = routes[routes["route_type"].isin([1, 2, 100, 109, 400])].copy()
    routes_ferrees = clean_route_colors(routes_ferrees)
    routes_ferrees["route_id"] = routes_ferrees["route_id"].astype(str)

    stop_times["HEURE_BRUTE"] = stop_times["arrival_time"].astype(str).str.split(":").str[0]
    stop_times = stop_times.dropna(subset=["HEURE_BRUTE"])
    stop_times["HEURE_BRUTE"] = pd.to_numeric(stop_times["HEURE_BRUTE"], errors="coerce")
    stop_times = stop_times.dropna(subset=["HEURE_BRUTE"])
    stop_times["HEURE_BRUTE"] = stop_times["HEURE_BRUTE"].astype(int)
    stop_times["HEURE"] = stop_times["HEURE_BRUTE"] % 24

    return routes, trips, stop_times, stops, routes_ferrees
