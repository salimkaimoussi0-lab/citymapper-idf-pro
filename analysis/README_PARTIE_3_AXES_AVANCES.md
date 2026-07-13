# Partie 3 — Analyses avancées

Scripts 11 à 15.

Objectif : pouls horaire du réseau, comparaison par ligne, CO2 évité, déserts ferroviaires et perturbations IDFM.

Commande de test :

for f in analysis/11_*.py analysis/12_*.py analysis/13_*.py analysis/14_*.py; do python "$f"; done

Pour IDFM :

export IDFM_API_KEY="ta_cle_idfm"
python analysis/15_axe3_perturbations_idfm.py
