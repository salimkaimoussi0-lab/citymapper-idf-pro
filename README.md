# Citymapper IDF - Production

Projet FastAPI + HTML/JS pour calculer des trajets Île-de-France.

## Fichiers importants

- `main.py` : backend FastAPI
- `index.html` : interface web
- `requirements.txt` : dépendances Python
- `.env.example` : exemple de variables d'environnement
- `data/referentiel-des-lignes.json` : fichier optionnel pour les couleurs exactes des lignes

## Lancer en local

```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate  # Windows PowerShell

pip install -r requirements.txt
cp .env.example .env
# Mets ta vraie clé dans .env : IDFM_API_KEY=...

uvicorn main:app --reload
```

Ouvre ensuite :

```text
http://127.0.0.1:8000
```

## Déploiement

Le projet contient déjà :

- `Procfile`
- `render.yaml`

Sur un serveur, ajoute la variable d'environnement :

```text
IDFM_API_KEY=ta_vraie_cle
```

Ne mets jamais la vraie clé API directement dans GitHub.
