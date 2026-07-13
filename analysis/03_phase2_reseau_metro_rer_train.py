import plotly.express as px
from _common import build_rail_network, save_fig

routes, trips, stop_times, stops, routes_ferrees, stop_to_route, stops_final, color_map = build_rail_network()

stops_finaux = stops_final.drop_duplicates(subset=["stop_id"]).copy()

print(f"Succès ! On a maintenant {len(stops_finaux)} stations ferrées détectées.")

fig = px.scatter_mapbox(
    stops_finaux,
    lat="stop_lat",
    lon="stop_lon",
    hover_name="stop_name",
    color_discrete_sequence=["#E2001A"],
    zoom=10,
    height=700,
)

fig.update_layout(
    mapbox_style="carto-positron",
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title="Phase 2 : Le Réseau du Métro & RER",
)

save_fig(fig, "03_phase2_reseau_metro_rer_train.html")
