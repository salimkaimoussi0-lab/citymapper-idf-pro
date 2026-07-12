import os
import json
from pathlib import Path

import pandas as pd
import requests

from _common import TABLEAUX_DIR, ensure_output_dirs


URL_INCIDENTS = "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/line_reports/line_reports?count=1000"


def main():
    ensure_output_dirs()

    api_key = os.getenv("IDFM_API_KEY", "").strip()

    if not api_key:
        raise RuntimeError(
            "Variable IDFM_API_KEY absente.\n"
            "Dans Git Bash : export IDFM_API_KEY='ta_cle_idfm'\n"
            "Sur Vercel : Settings > Environment Variables > IDFM_API_KEY"
        )

    print("Connexion IDFM / PRIM...")
    response = requests.get(URL_INCIDENTS, headers={"apiKey": api_key}, timeout=25)

    if response.status_code != 200:
        print("Erreur IDFM :", response.status_code)
        print(response.text[:1000])
        response.raise_for_status()

    payload = response.json()
    disruptions = payload.get("disruptions", [])

    rows = []

    for incident in disruptions:
        messages = incident.get("messages", [])
        texte_alerte = messages[0].get("text", "").replace("\n", " ").strip() if messages else "Sans description"

        severity = incident.get("severity", {})
        severity_name = severity.get("name") or severity.get("effect") or ""

        for obj in incident.get("impacted_objects", []):
            pt_obj = obj.get("pt_object", {})
            nom = pt_obj.get("name", "Inconnu")
            type_lieu = pt_obj.get("embedded_type", "")

            if type_lieu == "line":
                line = pt_obj.get("line", {})
                mode = line.get("commercial_mode", {}).get("name", "")
                code = line.get("code") or nom

                if mode in ["Métro", "RER", "Tramway", "Train"]:
                    rows.append(
                        {
                            "type": "Ligne",
                            "mode": mode,
                            "ligne": code,
                            "lieu": f"{mode} {code}",
                            "severite": severity_name,
                            "message": texte_alerte,
                        }
                    )

            elif type_lieu in ["stop_area", "stop_point"]:
                rows.append(
                    {
                        "type": "Gare / Station",
                        "mode": "",
                        "ligne": "",
                        "lieu": nom,
                        "severite": severity_name,
                        "message": texte_alerte,
                    }
                )

    df = pd.DataFrame(rows).drop_duplicates()

    csv_path = TABLEAUX_DIR / "06_perturbations_idfm.csv"
    json_path = TABLEAUX_DIR / "06_perturbations_idfm.json"

    df.to_csv(csv_path, index=False)
    json_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"OK perturbations récupérées : {len(df)}")
    print(f"CSV : {csv_path}")
    print(f"JSON : {json_path}")


if __name__ == "__main__":
    main()
