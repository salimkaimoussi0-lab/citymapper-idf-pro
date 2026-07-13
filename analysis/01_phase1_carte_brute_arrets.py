import plotly.express as px
from _common import read_gtfs, save_fig

print("Lecture des données en cours...")
stops = read_gtfs("stops.txt")
stops = stops.dropna(subset=["stop_lat", "stop_lon"])

print("Création de la carte brute des arrêts...")
fig = px.scatter_mapbox(
    stops,
    lat="stop_lat",
    lon="stop_lon",
    hover_name="stop_name",
    color_discrete_sequence=["#003399"],
    zoom=9,
    height=700,
)

fig.update_layout(
    mapbox_style="carto-positron",
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title="Phase 1 : Cartographie Brute de tous les arrêts d'Île-de-France",
)

save_fig(fig, "01_phase1_carte_brute_arrets.html")
