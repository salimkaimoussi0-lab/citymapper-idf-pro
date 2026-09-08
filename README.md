# Citymapper IDF Pro

Citymapper IDF Pro est un projet web et data centré sur l'analyse du réseau de transport en Ile-de-France.

Le projet combine une application web interactive, une API Python et un module complet d'analyse de données inspiré de Google Colab.

## Site en production

https://citymapper-idf-pro.vercel.app

## But du projet

L'objectif principal est de construire une plateforme capable de visualiser, analyser et comprendre le réseau de transport francilien.

Le projet ne se limite pas à afficher une carte. Il cherche aussi à exploiter les données de transport pour produire des indicateurs utiles :

- localisation des arrêts et stations ;
- visualisation du réseau ferré ;
- identification des grands hubs de correspondance ;
- analyse de la fréquentation Navigo ;
- calcul d'un indice de tension voyageurs / trains ;
- analyse horaire du pouls du réseau ;
- estimation de l'impact écologique ;
- détection des zones moins desservies ;
- récupération des perturbations temps réel IDFM.

Ce projet montre donc à la fois des compétences en développement web, backend Python, analyse de données, visualisation interactive et manipulation de données géographiques.

## Organisation générale

Le projet contient deux grandes parties.

### 1. Application web

L'application web est la partie visible du projet. Elle permet de présenter une interface cartographique accessible depuis un navigateur.

Elle utilise une interface HTML / CSS / JavaScript et une API Python pour connecter les données au site.

Fonctionnalités principales :

- affichage d'une carte interactive ;
- recherche de lieux, adresses ou stations ;
- affichage de points d'intérêt ;
- interface responsive ;
- connexion entre le front web et le backend Python ;
- déploiement en production avec Vercel.

### 2. Module d'analyse de données

Le dossier analysis contient les scripts Python séparés qui remplacent l'ancien notebook Google Colab.

Chaque script correspond à une étape précise de l'analyse. Les résultats sont générés sous forme de cartes HTML dynamiques, graphiques interactifs, tableaux CSV, fichiers Excel et tableaux HTML filtrables.

La commande principale pour lancer toutes les analyses est :

bash scripts/run_colab_style_analysis.sh

Le rapport global généré est :

reports/rapport_colab_style.html

## Technologies utilisées

### Langages

- Python ;
- JavaScript ;
- HTML ;
- CSS ;
- Bash.

### Backend et API

- FastAPI ;
- Uvicorn ;
- Python ;
- API Ile-de-France Mobilités / PRIM / Navitia.

### Frontend

- HTML ;
- CSS ;
- JavaScript ;
- interface cartographique web.

### Data analyse et visualisation

- pandas pour la manipulation des données ;
- Plotly Express pour les cartes et graphiques interactifs ;
- RapidFuzz pour le fuzzy matching entre les noms GTFS et Navigo ;
- GeoPandas pour les analyses géographiques ;
- Shapely pour la géométrie spatiale ;
- Requests pour les appels API ;
- OpenPyXL pour les exports Excel.

## Données utilisées

Le projet exploite plusieurs types de données :

- GTFS Ile-de-France Mobilités : arrêts, lignes, trajets, horaires ;
- validations Navigo : fréquentation moyenne par arrêt ;
- API IDFM / PRIM / Navitia : perturbations temps réel ;
- GeoJSON des communes d'Ile-de-France : analyse des zones desservies.

Les fichiers lourds restent en local et ne doivent pas être envoyés sur GitHub.

Fichiers attendus :

data/raw/IDFM-gtfs.zip
data/raw/validations_navigo.csv

## Structure du projet

citymapper_idf_production/
- app.py : point d'entrée API / backend.
- main.py : logique principale côté Python.
- index.html : interface web.
- vercel.json : configuration de déploiement Vercel.
- requirements.txt : dépendances du site web.
- requirements-analysis.txt : dépendances des analyses.
- analysis/ : scripts Python d'analyse séparés.
- scripts/ : scripts d'exécution et génération du rapport.
- data/ : dossier des données locales.
- reports/ : dossier des résultats générés localement.

## Tester le projet

Installer les dépendances d'analyse :

python -m pip install -r requirements-analysis.txt

Vérifier les scripts Python :

python -m py_compile analysis/*.py scripts/*.py

Tester la partie 1 :

for f in analysis/0[1-5]_*.py; do python "$f"; done

Tester la partie 2 :

for f in analysis/0[6-9]_*.py analysis/10_*.py; do python "$f"; done

Tester la partie 3 :

for f in analysis/11_*.py analysis/12_*.py analysis/13_*.py analysis/14_*.py; do python "$f"; done

Tester les perturbations IDFM :

export IDFM_API_KEY="ta_cle_idfm"
python analysis/15_axe3_perturbations_idfm.py

Commande principale pour tout tester :

bash scripts/run_colab_style_analysis.sh

## Résultats générés

Les analyses créent :

- des cartes HTML dynamiques dans reports/cartes/ ;
- des tableaux CSV et Excel dans reports/tableaux/ ;
- des tableaux HTML filtrables dans reports/html_tables/ ;
- un rapport global dans reports/rapport_colab_style.html.

## Déploiement

Le site web est déployé avec Vercel.

Lien production :

https://citymapper-idf-pro.vercel.app

## Sécurité

Ne jamais envoyer sur GitHub :

- les clés API ;
- les fichiers .env ;
- les données GTFS lourdes ;
- les validations Navigo brutes ;
- les rapports générés volumineux.

Les clés API doivent être utilisées avec des variables d'environnement.
