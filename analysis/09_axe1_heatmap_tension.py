import pandas as pd
import plotly.express as px
from _common import build_saturation_dataset, save_fig, TABLEAUX

stops_complet, routes, trips, stop_times, stops, routes_ferrees, stop_to_route, color_map = build_saturation_dataset()

print("1. Calcul de l'offre de transport : nombre de trains par quai...")

colonnes_a_nettoyer = ["NB_TRAINS", "INDICE_TENSION", "INDICE_AFFICHE"]
for col in colonnes_a_nettoyer:
    if col in stops_complet.columns:
        stops_complet.drop(columns=[col], inplace=True)

offre_transport = stop_times.groupby("stop_id")["trip_id"].count().reset_index()
offre_transport.rename(columns={"trip_id": "NB_TRAINS"}, inplace=True)

stops_complet = pd.merge(stops_complet, offre_transport, on="stop_id", how="left")
stops_complet["NB_TRAINS"] = stops_complet["NB_TRAINS"].fillna(1)

print("2. Calcul de l'indice de tension...")
stops_complet["INDICE_TENSION"] = stops_complet["NB_VALD"] / stops_complet["NB_TRAINS"]
stops_complet["INDICE_TENSION"] = stops_complet["INDICE_TENSION"].round(2)

df_carte = stops_complet[stops_complet["NB_VALD"] > 100].copy()

limite_haute = df_carte["INDICE_TENSION"].quantile(0.95)
df_carte["INDICE_AFFICHE"] = df_carte["INDICE_TENSION"].clip(upper=limite_haute)

print("3. Génération de la carte de crise...")

fig = px.scatter_mapbox(
    df_carte,
    lat="stop_lat",
    lon="stop_lon",
    hover_name="stop_name",
    hover_data={
        "INDICE_TENSION": True,
        "NB_VALD": ":.0f",
        "NB_TRAINS": True,
        "route_short_name": True,
        "INDICE_AFFICHE": False,
    },
    color="INDICE_AFFICHE",
    color_continuous_scale="YlOrRd",
    size="NB_VALD",
    size_max=35,
    zoom=11,
    height=800,
)

fig.update_layout(
    mapbox_style="carto-positron",
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title="AXE 1 : Heatmap de Tension (Couleur = Voyageurs par Train)",
    coloraxis_colorbar=dict(title="Tension<br>(Voyageurs/Train)"),
)

save_fig(fig, "09_axe1_heatmap_tension.html")

df_carte.to_excel(TABLEAUX / "Base_IDF_Axe1_Tension.xlsx", index=False)
df_carte.to_csv(TABLEAUX / "Base_IDF_Axe1_Tension.csv", index=False, encoding="utf-8-sig")

print("Export terminé : Base_IDF_Axe1_Tension.xlsx")
