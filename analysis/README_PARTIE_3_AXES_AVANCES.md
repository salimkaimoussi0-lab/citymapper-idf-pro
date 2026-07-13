# Partie 3 — Analyses avancées

Cette partie donne une dimension plus complète et plus professionnelle au projet.

Elle ajoute des analyses temporelles, écologiques, géographiques et temps réel.

## But

L'objectif est d'aller au-delà de la simple carte de transport pour produire des indicateurs d'aide à la décision.

## Scripts

### 11_axe2_pouls_reseau.py

Analyse le pouls global du réseau.

Le script compte le nombre de passages ou arrêts en gare par heure.

Il permet de visualiser les heures où le réseau est le plus actif.

### 12_axe2_pouls_par_ligne.py

Compare le pouls horaire par ligne.

Chaque ligne est affichée dans un graphique interactif, ce qui permet de comparer les rythmes de circulation.

### 13_axe2_co2_evite.py

Estime les tonnes de CO2 évitées grâce au transport ferroviaire.

Le calcul repose sur une comparaison simplifiée entre un trajet moyen en voiture et un trajet moyen en train.

Hypothèses utilisées :

- distance moyenne : 15 km ;
- voiture : 0.150 kg CO2 / km ;
- train : 0.005 kg CO2 / km.

### 14_axe2_deserts_ferroviaires.py

Identifie les communes moins desservies par le réseau ferré.

Le script utilise GeoPandas, Shapely et un GeoJSON des communes d'Ile-de-France.

Il effectue une jointure spatiale entre les gares et les communes.

### 15_axe3_perturbations_idfm.py

Récupère les perturbations temps réel depuis l'API IDFM / PRIM / Navitia.

Le script extrait les incidents liés aux lignes et aux gares.

La clé API doit être stockée dans une variable d'environnement.

## Commande de test

for f in analysis/11_*.py analysis/12_*.py analysis/13_*.py analysis/14_*.py; do python "$f"; done

## Tester les perturbations IDFM

export IDFM_API_KEY="ta_cle_idfm"
python analysis/15_axe3_perturbations_idfm.py
