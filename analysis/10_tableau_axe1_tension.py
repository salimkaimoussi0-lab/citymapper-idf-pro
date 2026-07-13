import pandas as pd
from _common import build_saturation_dataset, save_table

stops_complet, routes, trips, stop_times, stops, routes_ferrees, stop_to_route, color_map = build_saturation_dataset()

offre_transport = stop_times.groupby("stop_id")["trip_id"].count().reset_index()
offre_transport.rename(columns={"trip_id": "NB_TRAINS"}, inplace=True)

stops_complet = pd.merge(stops_complet, offre_transport, on="stop_id", how="left")
stops_complet["NB_TRAINS"] = stops_complet["NB_TRAINS"].fillna(1)
stops_complet["INDICE_TENSION"] = (stops_complet["NB_VALD"] / stops_complet["NB_TRAINS"]).round(2)

df_carte = stops_complet[stops_complet["NB_VALD"] > 100].copy()

colonnes_finales = [
    "stop_name",
    "route_short_name",
    "NB_VALD",
    "NB_TRAINS",
    "INDICE_TENSION",
]

tableau_colab = df_carte[colonnes_finales].sort_values(
    by="INDICE_TENSION",
    ascending=False,
).copy()

tableau_colab.columns = [
    "Station/Gare",
    "Ligne",
    "Voyageurs/Jour",
    "Trains/Jour",
    "Indice de Tension",
]

save_table(
    tableau_colab,
    "10_tableau_axe1_tension",
    "Tableau AXE 1 : classement des stations les plus tendues",
)
