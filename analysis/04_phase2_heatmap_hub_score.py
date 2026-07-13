import pandas as pd
import plotly.express as px
from _common import build_rail_network, save_fig

routes, trips, stop_times, stops, routes_ferrees, stop_to_route, stops_final, color_map = build_rail_network()

print("Calcul de l'affluence théorique Hub Score...")

hub_scores = (
    stop_to_route
    .groupby("stop_id")["route_short_name"]
    .nunique()
    .reset_index()
)

hub_scores.rename(columns={"route_short_name": "hub_score"}, inplace=True)

stops_final = pd.merge(stops_final, hub_scores, on="stop_id", how="left")
stops_final["hub_score"] = stops_final["hub_score"].fillna(1)

print("Prêt ! Les stations sont maintenant dimensionnées selon leur importance.")

fig = px.scatter_mapbox(
    stops_final,
    lat="stop_lat",
    lon="stop_lon",
    hover_name="stop_name",
    hover_data={
        "route_short_name": True,
        "hub_score": True,
        "stop_lat": False,
        "stop_lon": False,
    },
    color="route_short_name",
    color_discrete_map=color_map,
    size="hub_score",
    size_max=20,
    zoom=11,
    height=800,
)

fig.update_layout(
    mapbox_style="carto-positron",
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title="Phase 2 : Heatmap de Saturation (Taille = Nombre de correspondances)",
    legend_title_text="Lignes RATP/SNCF",
)

save_fig(fig, "04_phase2_heatmap_hub_score.html")
