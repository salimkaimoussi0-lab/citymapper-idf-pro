import plotly.express as px
from _common import build_saturation_dataset, save_fig

stops_complet, routes, trips, stop_times, stops, routes_ferrees, stop_to_route, color_map = build_saturation_dataset()

print("Génération de la carte finale de saturation réelle...")

fig = px.scatter_mapbox(
    stops_complet,
    lat="stop_lat",
    lon="stop_lon",
    hover_name="stop_name",
    hover_data={
        "NB_VALD": ":.0f",
        "route_short_name": True,
        "stop_lat": False,
        "stop_lon": False,
    },
    color="route_short_name",
    color_discrete_map=color_map,
    size="NB_VALD",
    size_max=25,
    zoom=11,
    height=800,
)

fig.update_layout(
    mapbox_style="carto-positron",
    title="PROJET : Saturation Réelle du Réseau IDF",
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    legend_title_text="Lignes RATP/SNCF",
)

save_fig(fig, "06_saturation_reelle_reseau_idf.html")
