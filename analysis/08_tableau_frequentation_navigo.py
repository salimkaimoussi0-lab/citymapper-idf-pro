from _common import build_saturation_dataset, save_table

stops_complet, routes, trips, stop_times, stops, routes_ferrees, stop_to_route, color_map = build_saturation_dataset()

colonnes_affichage = [
    "stop_name",
    "route_short_name",
    "NB_VALD",
    "nom_match_navigo",
]

tableau_interactif = (
    stops_complet[colonnes_affichage]
    .sort_values(by="NB_VALD", ascending=False)
    .copy()
)

tableau_interactif.columns = [
    "Nom de la Gare",
    "Ligne principale",
    "Voyageurs / Jour",
    "Match Navigo",
]

save_table(
    tableau_interactif,
    "08_tableau_frequentation_navigo",
    "Tableau interactif : fréquentation Navigo par gare",
)
