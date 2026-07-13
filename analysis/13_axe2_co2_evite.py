import plotly.express as px
from _common import build_saturation_dataset, save_fig, TABLEAUX, save_table

stops_complet, routes, trips, stop_times, stops, routes_ferrees, stop_to_route, color_map = build_saturation_dataset()

print("1. Calcul de l'Impact Écologique : tonnes de CO2 évitées...")

DISTANCE_MOYENNE_KM = 15
EMISSION_VOITURE_KG_KM = 0.150
EMISSION_TRAIN_KG_KM = 0.005

stops_complet["NB_VALD"] = stops_complet["NB_VALD"].fillna(0)

stops_complet["CO2_VOITURE_KG"] = (
    stops_complet["NB_VALD"] * DISTANCE_MOYENNE_KM * EMISSION_VOITURE_KG_KM
)

stops_complet["CO2_TRAIN_KG"] = (
    stops_complet["NB_VALD"] * DISTANCE_MOYENNE_KM * EMISSION_TRAIN_KG_KM
)

stops_complet["CO2_EVITE_TONNES"] = (
    stops_complet["CO2_VOITURE_KG"] - stops_complet["CO2_TRAIN_KG"]
) / 1000

stops_complet["CO2_EVITE_TONNES"] = stops_complet["CO2_EVITE_TONNES"].round(1)

print("2. Préparation du classement écologique...")

df_unique = stops_complet.drop_duplicates(subset=["nom_match_navigo"])
df_ecolo = (
    df_unique[df_unique["NB_VALD"] > 0]
    .sort_values(by="CO2_EVITE_TONNES", ascending=False)
    .head(20)
)

print("3. Génération du graphique...")

fig = px.bar(
    df_ecolo,
    x="CO2_EVITE_TONNES",
    y="stop_name",
    orientation="h",
    title="AXE 2 : Les 20 Gares les plus Écologiques (Tonnes de CO2 évitées / jour)",
    labels={
        "CO2_EVITE_TONNES": "Tonnes de CO2 sauvées par jour",
        "stop_name": "Gare / Station",
    },
    color="CO2_EVITE_TONNES",
    color_continuous_scale="Greens",
    text_auto=".1f",
)

fig.update_layout(
    yaxis={"categoryorder": "total ascending"},
    plot_bgcolor="white",
)

save_fig(fig, "13_axe2_co2_evite.html")

df_unique.to_excel(TABLEAUX / "Base_IDF_Complete_Avec_CO2.xlsx", index=False)
df_unique.to_csv(TABLEAUX / "Base_IDF_Complete_Avec_CO2.csv", index=False, encoding="utf-8-sig")

save_table(
    df_ecolo,
    "13_tableau_top20_co2_evite",
    "AXE 2 : Top 20 des gares les plus écologiques",
)

print("Données sauvegardées avec le nouvel indicateur CO2.")
