# Partie 1 — Cartographie et réseau

Cette partie correspond à la phase de découverte et de cartographie du réseau de transport.

## But

L'objectif est de partir des fichiers GTFS bruts pour visualiser les arrêts, identifier les lignes ferrées et comprendre la structure du réseau.

Cette étape est essentielle car elle prépare toutes les analyses suivantes.

## Données utilisées

- stops.txt : liste des arrêts et coordonnées GPS ;
- routes.txt : informations sur les lignes ;
- trips.txt : trajets associés aux lignes ;
- stop_times.txt : arrêts desservis par les trajets.

## Scripts

### 01_phase1_carte_brute_arrets.py

Crée une carte brute de tous les arrêts d'Ile-de-France.

Cette carte sert de première visualisation globale du volume de points présents dans les données GTFS.

### 02_phase15_reseau_interactif_couleurs.py

Affiche le réseau ferré avec les couleurs des lignes.

Ce script rend la carte plus lisible et plus proche d'une visualisation transport réelle.

### 03_phase2_reseau_metro_rer_train.py

Filtre les lignes ferrées principales : métro, RER, train et types GTFS équivalents.

Le but est de ne garder que le réseau structurant.

### 04_phase2_heatmap_hub_score.py

Calcule un hub score pour chaque station.

Le hub score correspond au nombre de lignes différentes desservant une station.

Plus le point est grand, plus la station joue un rôle de correspondance.

### 05_tableau_hubs_correspondances.py

Génère un tableau des plus grandes gares et stations selon le nombre de correspondances.

Ce tableau permet d'identifier les grands noeuds du réseau comme Gare du Nord, Gare de Lyon, Châtelet ou Nation.

## Commande de test

for f in analysis/0[1-5]_*.py; do python "$f"; done
