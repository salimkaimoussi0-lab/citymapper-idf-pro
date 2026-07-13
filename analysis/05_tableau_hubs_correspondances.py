import pandas as pd
from _common import build_rail_network, save_table

routes, trips, stop_times, stops, routes_ferrees, stop_to_route, stops_final, color_map = build_rail_network()

print("Création du tableau des hubs...")

donnees_tableau = pd.merge(
    stop_to_route,
    stops[["stop_id", "stop_name"]],
    on="stop_id",
    how="left",
)

tableau_hubs = donnees_tableau.groupby("stop_name").agg(
    Nombre_Correspondances=("route_short_name", "nunique"),
    Lignes_Desservies=("route_short_name", lambda x: ", ".join(sorted(x.astype(str).unique()))),
).reset_index()

tableau_hubs = tableau_hubs.sort_values(
    by="Nombre_Correspondances",
    ascending=False,
).reset_index(drop=True)

tableau_hubs.rename(
    columns={"stop_name": "Nom de la Gare / Station"},
    inplace=True,
)

save_table(
    tableau_hubs.head(140),
    "05_tableau_hubs_top_140",
    "Tableau hubs : 140 plus grandes gares / stations par correspondances",
)
