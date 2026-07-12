#!/usr/bin/env bash
set -e

echo "Installation des dépendances d'analyse..."
python -m pip install -r requirements-analysis.txt

echo ""
echo "1/6 Carte réseau"
python analysis/01_build_network_map.py

echo ""
echo "2/6 Hubs / correspondances"
python analysis/02_build_hubs_ranking.py

echo ""
echo "3/6 Saturation Navigo"
python analysis/03_build_saturation_navigo.py

echo ""
echo "4/6 Indice de tension"
python analysis/04_build_tension_index.py

echo ""
echo "5/6 Pouls horaire"
python analysis/05_build_hourly_network_pulse.py

echo ""
echo "6/6 Perturbations IDFM"
if [ -z "$IDFM_API_KEY" ]; then
  echo "IDFM_API_KEY absente : script perturbations ignoré."
else
  python analysis/06_fetch_idfm_disruptions.py
fi

echo ""
echo "Analyse terminée."
echo "Cartes : reports/cartes/"
echo "Tableaux : reports/tableaux/"
