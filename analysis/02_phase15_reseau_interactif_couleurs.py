import plotly.express as px
from _common import build_rail_network, save_fig

routes, trips, stop_times, stops, routes_ferrees, stop_to_route, stops_final, color_map = build_rail_network()

print(f"Prêt ! Affichage de {len(stops_final)} stations avec légende interactive.")

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
    zoom=10,
    height=750,
)

fig.update_layout(
    mapbox_style="carto-positron",
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title="Phase 1.5 : Réseau Interactif RATP / SNCF",
    legend_title_text="Lignes RATP/SNCF",
)

save_fig(fig, "02_phase15_reseau_interactif_ratp_sncf.html")
