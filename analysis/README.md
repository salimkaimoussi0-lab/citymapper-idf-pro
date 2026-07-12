# Analyses trafic Ile-de-France

Ce dossier transforme l'ancien notebook Colab en scripts Python propres.

## Scripts

- 01_build_network_map.py : genere une carte interactive des arrets et lignes ferrees IDF.
- 02_build_hubs_ranking.py : classe les gares/stations par nombre de correspondances.
- 03_build_saturation_navigo.py : croise GTFS et validations Navigo pour visualiser la saturation reelle.
- 04_build_tension_index.py : calcule l'indice de tension = validations Navigo / trains.
- 05_build_hourly_network_pulse.py : calcule le pouls du reseau par heure et par ligne.
- 06_fetch_idfm_disruptions.py : recupere les perturbations IDFM / PRIM avec IDFM_API_KEY.

## Donnees attendues

Les fichiers lourds doivent rester en local :

- data/raw/IDFM-gtfs.zip
- data/raw/validations_navigo.csv

Ils ne sont pas versionnes dans GitHub.

## Lancement

bash scripts/run_all_analysis.sh

Pour les perturbations IDFM :

export IDFM_API_KEY="ta_cle_idfm"
python analysis/06_fetch_idfm_disruptions.py
