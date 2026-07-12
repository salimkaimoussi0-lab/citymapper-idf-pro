from pathlib import Path
import os
import re
import zipfile
import unicodedata

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"
CARTES_DIR = REPORTS_DIR / "cartes"
TABLEAUX_DIR = REPORTS_DIR / "tableaux"

FERROUS_ROUTE_TYPES = {"1", "2", "100", "109", "400"}


def ensure_output_dirs():
    CARTES_DIR.mkdir(parents=True, exist_ok=True)
    TABLEAUX_DIR.mkdir(parents=True, exist_ok=True)


def find_data_file(filename: str) -> Path:
    candidates = [
        PROJECT_ROOT / "data" / "raw" / filename,
        PROJECT_ROOT / "data" / filename,
        PROJECT_ROOT / "données" / filename,
        PROJECT_ROOT / filename,
        Path.home() / "Downloads" / filename,
    ]

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        f"Fichier introuvable : {filename}\n"
        "Mets-le dans data/raw/ ou dans Downloads.\n"
        f"Exemple attendu : {PROJECT_ROOT / 'data' / 'raw' / filename}"
    )


def read_gtfs_table(zip_path: Path, table_name: str, usecols=None) -> pd.DataFrame:
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"Ce fichier n'est pas un ZIP GTFS valide : {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as z:
        if table_name not in z.namelist():
            raise FileNotFoundError(f"{table_name} introuvable dans {zip_path}")

        return pd.read_csv(
            z.open(table_name),
            usecols=usecols,
            dtype=str,
            low_memory=False,
        )


def normalize_text(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip().upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_route_color(value) -> str:
    text = str(value or "").strip().replace("#", "")

    if not text or text.lower() == "nan":
        return "#777777"

    text = text[:6].upper()

    if len(text) != 6 or not re.fullmatch(r"[0-9A-F]{6}", text):
        return "#777777"

    return "#" + text


def filter_ferrous_routes(routes: pd.DataFrame) -> pd.DataFrame:
    routes = routes.copy()

    if "route_type" not in routes.columns:
        return routes

    routes["route_type"] = routes["route_type"].astype(str)
    return routes[routes["route_type"].isin(FERROUS_ROUTE_TYPES)].copy()


def load_network_tables(gtfs_zip: Path):
    stops = read_gtfs_table(gtfs_zip, "stops.txt")
    routes = read_gtfs_table(gtfs_zip, "routes.txt")
    trips = read_gtfs_table(gtfs_zip, "trips.txt", usecols=["route_id", "trip_id"])
    stop_times = read_gtfs_table(gtfs_zip, "stop_times.txt", usecols=["trip_id", "stop_id"])

    stops["stop_id"] = stops["stop_id"].astype(str)
    trips["trip_id"] = trips["trip_id"].astype(str)
    trips["route_id"] = trips["route_id"].astype(str)
    stop_times["trip_id"] = stop_times["trip_id"].astype(str)
    stop_times["stop_id"] = stop_times["stop_id"].astype(str)
    routes["route_id"] = routes["route_id"].astype(str)

    routes = filter_ferrous_routes(routes)
    routes["route_short_name"] = routes["route_short_name"].fillna("").astype(str)
    routes["route_color"] = routes.get("route_color", "").apply(clean_route_color)

    return stops, routes, trips, stop_times


def build_stop_line_table(gtfs_zip: Path) -> pd.DataFrame:
    stops, routes, trips, stop_times = load_network_tables(gtfs_zip)

    trips_routes = trips.merge(
        routes[["route_id", "route_short_name", "route_color"]],
        on="route_id",
        how="inner",
    )

    stop_lines = stop_times.merge(trips_routes, on="trip_id", how="inner")

    stop_lines = stop_lines.drop_duplicates(
        subset=["stop_id", "route_short_name"]
    )

    result = stops.merge(
        stop_lines[["stop_id", "route_short_name", "route_color"]],
        on="stop_id",
        how="inner",
    )

    result = result.dropna(subset=["stop_lat", "stop_lon"])
    result["stop_lat"] = pd.to_numeric(result["stop_lat"], errors="coerce")
    result["stop_lon"] = pd.to_numeric(result["stop_lon"], errors="coerce")
    result = result.dropna(subset=["stop_lat", "stop_lon"])

    return result


def detect_column(df: pd.DataFrame, possible_names):
    normalized = {normalize_text(c): c for c in df.columns}

    for name in possible_names:
        key = normalize_text(name)
        if key in normalized:
            return normalized[key]

    for c in df.columns:
        c_norm = normalize_text(c)
        for name in possible_names:
            if normalize_text(name) in c_norm:
                return c

    raise KeyError(f"Colonne introuvable. Colonnes disponibles : {list(df.columns)}")


def clean_number_series(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.replace("\u202f", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.extract(r"([0-9]+(?:\.[0-9]+)?)")[0]
    )
    return pd.to_numeric(cleaned, errors="coerce")
