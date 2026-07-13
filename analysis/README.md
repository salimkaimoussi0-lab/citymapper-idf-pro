# Analyses Citymapper IDF Pro

Ce dossier contient les scripts Python d'analyse du projet Citymapper IDF Pro.

Ces scripts remplacent l'ancien notebook Google Colab par une structure professionnelle, séparée, lisible et testable.

Chaque fichier correspond à une étape précise du raisonnement data.

## Objectif du module d'analyse

Le but est d'exploiter les données de transport franciliennes pour produire des indicateurs visuels et quantitatifs sur le réseau.

Les analyses permettent de répondre à plusieurs questions :

- Où se trouvent les arrêts et stations ?
- Quelles sont les lignes ferrées principales ?
- Quelles stations jouent le rôle de hubs ?
- Quelles gares ont la plus forte fréquentation Navigo ?
- Quelles stations sont les plus tendues par rapport à l'offre de trains ?
- A quelles heures le réseau est-il le plus actif ?
- Quelles lignes ont le plus de passages ?
- Quel impact écologique peut être estimé grâce au transport collectif ?
- Quelles communes sont moins desservies par le réseau ferroviaire ?
- Quelles perturbations sont visibles en temps réel via IDFM ?

## Partie 1 : cartographie et réseau

Scripts 01 à 05.

Cette partie charge les données GTFS, affiche les arrêts, filtre le réseau ferré et calcule les hubs de correspondance.

Elle permet de construire la première compréhension géographique du réseau.

## Partie 2 : saturation Navigo et tension

Scripts 06 à 10.

Cette partie croise les données GTFS avec les validations Navigo.

Elle utilise RapidFuzz pour faire correspondre les noms de stations entre deux sources de données différentes.

Elle produit ensuite une carte de saturation réelle et un indice de tension basé sur le rapport voyageurs / trains.

## Partie 3 : analyses avancées

Scripts 11 à 15.

Cette partie ajoute des indicateurs plus avancés : pouls horaire du réseau, comparaison par ligne, CO2 évité, déserts ferroviaires et perturbations temps réel.

## Commande principale

bash scripts/run_colab_style_analysis.sh

## Résultats

Les scripts génèrent des fichiers dans :

- reports/cartes/ ;
- reports/tableaux/ ;
- reports/html_tables/ ;
- reports/rapport_colab_style.html.
