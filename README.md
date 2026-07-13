# Citymapper IDF Pro

Site web de cartographie et d'analyse du réseau de transport en Ile-de-France.

## Site en production

https://citymapper-idf-pro.vercel.app

## Objectif du projet

Ce projet contient deux grandes parties :

1. Un site web interactif déployé en ligne.
2. Un module d'analyses avancées inspiré de Google Colab, avec cartes dynamiques, graphiques interactifs et tableaux filtrables.

## Fonctionnalités du site web

- Carte interactive de l'Ile-de-France.
- Recherche de lieux, adresses et stations.
- Visualisation de points d'intérêt.
- Interface web responsive.
- API Python connectée au front web.

## Fonctionnalités des analyses

Le dossier analysis contient les scripts Python séparés du projet.

Les analyses génèrent :

- cartes Plotly interactives ;
- graphiques dynamiques ;
- tableaux CSV ;
- fichiers Excel ;
- tableaux HTML filtrables ;
- rapport global façon Colab.

## Technologies utilisées

Langages : Python, JavaScript, HTML, CSS, Bash.

Backend : FastAPI, Uvicorn, Python.

Frontend : HTML, CSS, JavaScript.

Analyse de données : pandas, Plotly Express, RapidFuzz, GeoPandas, Shapely, Requests, OpenPyXL.

Données : GTFS Ile-de-France Mobilités, validations Navigo, perturbations IDFM PRIM Navitia, GeoJSON des communes IDF.

## Données locales nécessaires

Les fichiers lourds doivent rester en local :

data/raw/IDFM-gtfs.zip
data/raw/validations_navigo.csv

## Installation

python -m pip install -r requirements-analysis.txt

## Vérifier les scripts

python -m py_compile analysis/*.py scripts/*.py

## Tester la partie 1

for f in analysis/0[1-5]_*.py; do python "$f"; done

## Tester la partie 2

for f in analysis/0[6-9]_*.py analysis/10_*.py; do python "$f"; done

## Tester la partie 3

for f in analysis/11_*.py analysis/12_*.py analysis/13_*.py analysis/14_*.py; do python "$f"; done

## Tester les perturbations IDFM

export IDFM_API_KEY="ta_cle_idfm"
python analysis/15_axe3_perturbations_idfm.py

## Commande principale pour tout tester

bash scripts/run_colab_style_analysis.sh

Le rapport global généré est :

reports/rapport_colab_style.html

## Déploiement

Le site est déployé avec Vercel :

https://citymapper-idf-pro.vercel.app

## Sécurité

Ne jamais envoyer sur GitHub les clés API, fichiers .env, données GTFS lourdes, validations Navigo brutes ou rapports volumineux.
