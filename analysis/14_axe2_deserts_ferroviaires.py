import pandas as pd
import geopandas as gpd
import plotly.express as px
from shapely.geometry import Point
from _common import read_gtfs, save_fig, save_table

print("1. Filtrage strict : uniquement RER, Métro, Tram et Train...")

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

lignes_lourdes = routes[routes["route_type"].isin([0, 1, 2])]
trajets_lourds = trips[trips["route_id"].isin(lignes_lourdes["route_id"])]
arrets_lourds = stop_times[stop_times["trip_id"].isin(trajets_lourds["trip_id"])]

id_gares_lourdes = arrets_lourds["stop_id"].unique()
vraies_gares = stops[stops["stop_id"].isin(id_gares_lourdes)].copy()
vraies_gares = vraies_gares.dropna(subset=["stop_lat", "stop_lon"])

print(f"Nombre de gares ferroviaires conservées : {len(vraies_gares)}")

print("2. Téléchargement des frontières des communes d'Île-de-France...")

url_geojson = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions/ile-de-france/communes-ile-de-france.geojson"
communes_idf = gpd.read_file(url_geojson)

print("3. Croisement spatial : quelle gare est dans quelle ville ?")

geometrie_gares = [
    Point(xy)
    for xy in zip(vraies_gares["stop_lon"], vraies_gares["stop_lat"])
]

gares_geo = gpd.GeoDataFrame(
    vraies_gares,
    geometry=geometrie_gares,
    crs="EPSG:4326",
)

jointure_spatiale = gpd.sjoin(
    communes_idf,
    gares_geo,
    how="left",
    predicate="contains",
)

comptage_gares = jointure_spatiale.groupby("nom")["index_right"].count().reset_index()
comptage_gares.rename(columns={"index_right": "NB_GARES", "nom": "Commune"}, inplace=True)

communes_finales = communes_idf.merge(comptage_gares, left_on="nom", right_on="Commune")
communes_finales = communes_finales.set_index("Commune")

print("4. Génération de la carte des vrais déserts ferroviaires...")

fig = px.choropleth_mapbox(
    communes_finales,
    geojson=communes_finales.geometry,
    locations=communes_finales.index,
    color="NB_GARES",
    color_continuous_scale="Reds_r",
    mapbox_style="carto-positron",
    zoom=7.5,
    center={"lat": 48.8566, "lon": 2.3522},
    opacity=0.6,
    title="AXE 2 : Les Déserts (Uniquement Métro, RER, Tram, Train)",
    labels={"NB_GARES": "Nombre de gares/stations"},
)

fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

save_fig(fig, "14_axe2_deserts_ferroviaires.html")

save_table(
    comptage_gares.sort_values(by="NB_GARES", ascending=True),
    "14_tableau_deserts_ferroviaires",
    "AXE 2 : nombre de gares / stations par commune",
)
