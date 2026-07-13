import os
import sys
import requests
import pandas as pd
from _common import save_table

print("Connexion aux serveurs d'Île-de-France Mobilités...")

API_KEY = os.environ.get("IDFM_API_KEY")

if not API_KEY:
    print("Erreur : variable IDFM_API_KEY absente.")
    print("Dans Git Bash, lance :")
    print('export IDFM_API_KEY="ta_cle_idfm"')
    sys.exit(1)

url_incidents = "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/line_reports/line_reports?count=1000"
headers = {"apiKey": API_KEY}

try:
    reponse = requests.get(url_incidents, headers=headers, timeout=30)

    if reponse.status_code == 200:
        donnees = reponse.json()
        perturbations = donnees.get("disruptions", [])

        liste_incidents_propres = []

        for incident in perturbations:
            messages = incident.get("messages", [])
            texte_alerte = (
                messages[0].get("text", "").replace("\n", " ").strip()
                if messages
                else "Sans description"
            )

            for obj in incident.get("impacted_objects", []):
                pt_obj = obj.get("pt_object", {})
                nom = pt_obj.get("name", "Inconnu")
                type_lieu = pt_obj.get("embedded_type", "")

                if type_lieu == "line":
                    mode = (
                        pt_obj
                        .get("line", {})
                        .get("commercial_mode", {})
                        .get("name", "")
                    )

                    if mode in ["Métro", "RER", "Tramway", "Train"]:
                        liste_incidents_propres.append({
                            "Type": "Ligne",
                            "Lieu Exact": f"{mode} {nom}",
                            "Problème": texte_alerte,
                        })

                elif type_lieu in ["stop_area", "stop_point"]:
                    liste_incidents_propres.append({
                        "Type": "Gare / Station",
                        "Lieu Exact": nom,
                        "Problème": texte_alerte,
                    })

        df_incidents = pd.DataFrame(liste_incidents_propres)

        if not df_incidents.empty:
            df_incidents = df_incidents.drop_duplicates()

        print(f"Extraction réussie ! {len(df_incidents)} alertes détaillées récupérées.")

        save_table(
            df_incidents,
            "15_perturbations_idfm",
            "AXE 3 : perturbations temps réel IDFM",
        )

    else:
        print(f"Erreur API : Code {reponse.status_code}")
        print(reponse.text[:500])

except Exception as e:
    print(f"Le code a planté : {e}")
