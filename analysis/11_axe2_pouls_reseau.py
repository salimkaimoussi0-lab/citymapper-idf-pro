import plotly.express as px
from _common import load_temporal_data, save_fig, save_table

routes, trips, stop_times, stops, routes_ferrees = load_temporal_data()

print("Calcul de l'affluence du réseau...")

trains_par_heure = stop_times.groupby("HEURE")["trip_id"].count().reset_index()
trains_par_heure.rename(columns={"trip_id": "NOMBRE_DE_TRAINS"}, inplace=True)

print("Création du graphique : Le Pouls du Réseau...")

fig = px.bar(
    trains_par_heure,
    x="HEURE",
    y="NOMBRE_DE_TRAINS",
    labels={
        "HEURE": "Heure de la journée",
        "NOMBRE_DE_TRAINS": "Trains en circulation (Arrêts en gare)",
    },
    title="AXE 2 : Le Pouls du Réseau (Offre de trains par heure en Île-de-France)",
    color="NOMBRE_DE_TRAINS",
    color_continuous_scale="Turbo",
    text_auto=".2s",
)

fig.update_layout(
    xaxis=dict(tickmode="linear", tick0=0, dtick=1),
    plot_bgcolor="white",
    margin={"r": 20, "t": 50, "l": 20, "b": 20},
)

save_fig(fig, "11_axe2_pouls_reseau.html")

save_table(
    trains_par_heure,
    "11_tableau_pouls_reseau",
    "AXE 2 : nombre de trains / arrêts en gare par heure",
)
