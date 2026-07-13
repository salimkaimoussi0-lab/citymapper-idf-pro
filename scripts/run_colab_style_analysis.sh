#!/usr/bin/env bash
set -e

echo "Lancement des analyses Citymapper IDF Pro..."

python analysis/01_phase1_carte_brute_arrets.py
python analysis/02_phase15_reseau_interactif_couleurs.py
python analysis/03_phase2_reseau_metro_rer_train.py
python analysis/04_phase2_heatmap_hub_score.py
python analysis/05_tableau_hubs_correspondances.py
python analysis/06_saturation_reelle_navigo.py
python analysis/07_base_finale_saturation.py
python analysis/08_tableau_frequentation_navigo.py
python analysis/09_axe1_heatmap_tension.py
python analysis/10_tableau_axe1_tension.py
python analysis/11_axe2_pouls_reseau.py
python analysis/12_axe2_pouls_par_ligne.py
python analysis/13_axe2_co2_evite.py
python analysis/14_axe2_deserts_ferroviaires.py

if [ -n "$IDFM_API_KEY" ]; then
  python analysis/15_axe3_perturbations_idfm.py
else
  echo "Perturbations IDFM ignorées : IDFM_API_KEY non définie."
fi

python scripts/build_report_index.py
