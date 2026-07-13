import pandas as pd
import plotly.express as px
from _common import load_temporal_data, save_fig, save_table

routes, trips, stop_times, stops, routes_ferrees = load_temporal_data()

print("1. Fusion des données temporelles avec l'identité des lignes...")

df_temporel = pd.merge(
    stop_times,
    trips[["trip_id", "route_id"]],
    on="trip_id",
    how="left",
)

df_temporel = pd.merge(
    df_temporel,
    routes_ferrees[["route_id", "route_short_name", "route_color"]],
    on="route_id",
    how="left",
)

df_temporel = df_temporel.dropna(subset=["route_short_name"])

print("2. Calcul de l'affluence par ligne et par heure...")

pouls_par_ligne = (
    df_temporel
    .groupby(["HEURE", "route_short_name", "route_color"])["trip_id"]
    .count()
    .reset_index()
)

pouls_par_ligne.rename(columns={"trip_id": "NOMBRE_DE_TRAINS"}, inplace=True)

color_map = dict(zip(pouls_par_ligne["route_short_name"], pouls_par_ligne["route_color"]))

print("3. Création du graphique comparatif...")

fig = px.line(
    pouls_par_ligne,
    x="HEURE",
    y="NOMBRE_DE_TRAINS",
    color="route_short_name",
    color_discrete_map=color_map,
    title="AXE 2 : Comparaison du Pouls par Ligne",
    labels={
        "HEURE": "Heure de la journée",
        "NOMBRE_DE_TRAINS": "Trains (Arrêts en gare)",
        "route_short_name": "Lignes",
    },
    markers=True,
)

fig.update_layout(
    xaxis=dict(tickmode="linear", tick0=0, dtick=1),
    plot_bgcolor="white",
    hovermode="x unified",
    margin={"r": 20, "t": 50, "l": 20, "b": 20},
)

save_fig(fig, "12_axe2_pouls_par_ligne.html")

save_table(
    pouls_par_ligne,
    "12_tableau_pouls_par_ligne",
    "AXE 2 : pouls du réseau par ligne et par heure",
)
