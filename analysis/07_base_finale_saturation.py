import plotly.express as px
from _common import build_saturation_dataset, save_fig, TABLEAUX

stops_complet, routes, trips, stop_times, stops, routes_ferrees, stop_to_route, color_map = build_saturation_dataset()

excel_path = TABLEAUX / "Base_De_Donnees_Finale_Projet.xlsx"
csv_path = TABLEAUX / "Base_De_Donnees_Finale_Projet.csv"

stops_complet.to_excel(excel_path, index=False)
stops_complet.to_csv(csv_path, index=False, encoding="utf-8-sig")

print("Fichier Excel sauvegardé :", excel_path)
print("Fichier CSV sauvegardé :", csv_path)

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
    size_max=30,
    zoom=11,
    height=800,
)

fig.update_layout(
    mapbox_style="carto-positron",
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title="Saturation Réelle : Millions de Validations Navigo",
    legend_title_text="Lignes",
)

save_fig(fig, "07_base_finale_saturation_reelle.html")
