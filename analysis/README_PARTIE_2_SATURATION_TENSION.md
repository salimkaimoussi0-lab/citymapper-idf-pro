# Partie 2 — Saturation Navigo et indice de tension

Cette partie ajoute une dimension fréquentation au projet.

Elle ne se contente plus de montrer le réseau. Elle cherche à comprendre où le réseau est le plus utilisé et où la tension est la plus forte.

## But

L'objectif est de croiser les stations du GTFS avec les validations Navigo pour obtenir une estimation de la fréquentation réelle.

Ensuite, le projet compare cette fréquentation avec l'offre de trains pour produire un indicateur de tension.

## Méthode

1. Chargement des données GTFS.
2. Chargement du fichier validations_navigo.csv.
3. Moyenne des validations par arrêt.
4. Correspondance entre les noms GTFS et Navigo avec RapidFuzz.
5. Création d'une base finale enrichie.
6. Calcul de l'offre de trains par station.
7. Calcul de l'indice de tension.

Formule utilisée :

INDICE_TENSION = NB_VALD / NB_TRAINS

## Scripts

### 06_saturation_reelle_navigo.py

Crée une carte de saturation réelle du réseau IDF.

La taille des points dépend du nombre moyen de validations Navigo.

### 07_base_finale_saturation.py

Génère la base finale du projet avec les stations, les lignes, les validations Navigo et les correspondances de noms.

Exports produits : CSV et Excel.

### 08_tableau_frequentation_navigo.py

Crée un tableau interactif des gares les plus fréquentées.

Le tableau contient le nom de la gare, la ligne principale, le nombre de voyageurs par jour et le nom Navigo associé.

### 09_axe1_heatmap_tension.py

Crée une carte de tension.

La couleur représente le niveau de tension voyageurs / trains.

La taille représente le volume de voyageurs.

### 10_tableau_axe1_tension.py

Crée un classement des stations les plus tendues.

Ce tableau permet de repérer les zones où la fréquentation est élevée par rapport à l'offre disponible.

## Commande de test

for f in analysis/0[6-9]_*.py analysis/10_*.py; do python "$f"; done
