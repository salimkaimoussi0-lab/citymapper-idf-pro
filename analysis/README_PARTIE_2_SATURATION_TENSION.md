# Partie 2 — Saturation Navigo et tension

Scripts 06 à 10.

Objectif : croiser GTFS et validations Navigo avec RapidFuzz, générer une carte de saturation réelle et calculer l'indice de tension.

Commande de test :

for f in analysis/0[6-9]_*.py analysis/10_*.py; do python "$f"; done
