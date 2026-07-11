from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pathlib import Path
import json
import os
import re
import requests
import unicodedata
from difflib import SequenceMatcher


app = FastAPI(title="Citymapper IDF Pro - OpenFreeMap")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
DOSSIER_LOGOS = Path(os.getenv("LOGOS_DIR", BASE_DIR / "logos"))
FICHIER_LIGNES = Path(os.getenv("FICHIER_LIGNES", DATA_DIR / "referentiel-des-lignes.json"))

DOSSIER_LOGOS.mkdir(parents=True, exist_ok=True)
app.mount("/logos", StaticFiles(directory=str(DOSSIER_LOGOS)), name="logos")


API_KEY = os.getenv("IDFM_API_KEY", "").strip()
IDFM_HEADERS = {"apiKey": API_KEY} if API_KEY else {}

DICTIONNAIRE_COULEURS = {}


def normaliser_texte(texte):
    texte = str(texte or "").lower().strip()
    texte = "".join(
        caractere
        for caractere in unicodedata.normalize("NFD", texte)
        if unicodedata.category(caractere) != "Mn"
    )
    texte = re.sub(r"[^a-z0-9]+", " ", texte)
    texte = re.sub(r"\s+", " ", texte).strip()
    return texte


def nettoyer_requete_utilisateur(q):
    q = str(q or "").strip()

    # Corrige les écritures fréquentes : 8ter -> 8 ter, 8  ter -> 8 ter
    q = re.sub(r"\b(\d+)\s*(bis|ter|quater)\b", r"\1 \2", q, flags=re.IGNORECASE)

    # Petites corrections utiles sans imposer une ville.
    q = q.replace("pepinieres", "pépinières")
    q = q.replace("pepinières", "pépinières")
    q = q.replace("pepiniers", "pépinières")

    q = re.sub(r"\s+", " ", q).strip()
    return q



MOTS_FAIBLES_RECHERCHE = {
    "rue", "avenue", "av", "boulevard", "bd", "place", "impasse", "chemin",
    "route", "allee", "allée", "quai", "square", "cours", "passage",
    "de", "du", "des", "la", "le", "les", "l", "d", "a", "au", "aux",
    "bis", "ter", "quater"
}


def mots_significatifs_recherche(query):
    q = normaliser_texte(query)

    mots = []

    for mot in q.split():
        if mot.isdigit():
            continue

        if mot in MOTS_FAIBLES_RECHERCHE:
            continue

        if len(mot) < 2:
            continue

        mots.append(mot)

    return mots


def texte_contient_mot_ou_prefixe(texte, mot):
    texte = normaliser_texte(texte)
    mot = normaliser_texte(mot)

    if not mot:
        return True

    mots_texte = texte.split()

    return any(m.startswith(mot) or mot.startswith(m) for m in mots_texte)


def resultat_recherche_coherent(query, item):
    """
    Empêche les résultats absurdes.
    Exemple : "8 ter rue des pe" ne doit pas afficher "Rue des Juges Consuls".
    """
    query = str(query or "").strip()

    if not query:
        return True

    item_type = item.get("type", "")
    texte_resultat = " ".join([
        str(item.get("title", "")),
        str(item.get("subtitle", "")),
        str(item.get("detail", ""))
    ])

    mots = mots_significatifs_recherche(query)

    if not mots:
        return True

    dernier_mot = mots[-1]
    recherche_adresse = item_type == "address" or contient_numero_adresse(query)

    if recherche_adresse:
        # Si l'utilisateur tape le début de la vraie rue, le résultat doit contenir ce début.
        # "pe" => Pépinières OK, Juges Consuls NON.
        if len(dernier_mot) >= 2 and not texte_contient_mot_ou_prefixe(texte_resultat, dernier_mot):
            return False

        # Les mots déjà complets doivent aussi être cohérents.
        for mot in mots[:-1]:
            if len(mot) >= 4 and not texte_contient_mot_ou_prefixe(texte_resultat, mot):
                return False

        return True

    # Pour les gares / lieux, on garde aussi une logique minimale.
    if len(dernier_mot) >= 3 and not texte_contient_mot_ou_prefixe(texte_resultat, dernier_mot):
        return False

    return True


def contient_numero_adresse(query):
    return bool(re.search(r"\b\d+[a-zA-Z]?\b", str(query or "")))


def semble_recherche_gare(query):
    q = normaliser_texte(query)
    mots_gare = ["gare", "station", "rer", "metro", "métro", "tram", "bus", "terminus", "aeroport", "aéroport"]
    return any(mot in q for mot in mots_gare)


def semble_recherche_lieu(query):
    q = normaliser_texte(query)
    mots_lieu = [
        "tour", "musee", "musée", "palais", "chateau", "château", "arc",
        "hotel", "hôtel", "hopital", "hôpital", "clinique", "parc", "jardin",
        "universite", "université", "stade", "centre", "monument", "eglise",
        "église", "bibliotheque", "bibliothèque"
    ]
    return any(mot in q for mot in mots_lieu)


def score_texte(query, texte):
    query = normaliser_texte(query)
    texte = normaliser_texte(texte)

    if not query or not texte:
        return 0

    if texte == query:
        return 120

    if texte.startswith(query):
        return 105

    if query in texte:
        return 90

    mots_query = [mot for mot in query.split(" ") if len(mot) > 1]
    score_mots = sum(12 for mot in mots_query if mot in texte)
    ratio = int(SequenceMatcher(None, query, texte).ratio() * 70)

    return ratio + score_mots


def ajouter_resultat_unique(resultats, item):
    query_filtre = item.pop("_query_filtre", None)

    if query_filtre and not resultat_recherche_coherent(query_filtre, item):
        return

    if not item.get("title") or item.get("lon") is None or item.get("lat") is None:
        return

    cle = (
        normaliser_texte(item.get("title", "")),
        normaliser_texte(item.get("subtitle", "")),
        round(float(item.get("lon", 0)), 5),
        round(float(item.get("lat", 0)), 5)
    )

    for resultat in resultats:
        cle_existante = (
            normaliser_texte(resultat.get("title", "")),
            normaliser_texte(resultat.get("subtitle", "")),
            round(float(resultat.get("lon", 0)), 5),
            round(float(resultat.get("lat", 0)), 5)
        )

        if cle == cle_existante:
            return

    resultats.append(item)


def type_osm_et_libelle(category, osm_type, extratags):
    category = str(category or "").lower()
    osm_type = str(osm_type or "").lower()
    extratags = extratags or {}

    if category == "tourism" or osm_type in ("museum", "attraction", "monument", "memorial", "viewpoint"):
        return "monument", "Lieu culturel"

    if extratags.get("wikipedia"):
        return "monument", "Lieu connu"

    if category == "amenity" and osm_type in ("hospital", "clinic", "doctors"):
        return "health", "Santé"

    if category == "amenity" and osm_type == "pharmacy":
        return "health", "Pharmacie"

    if category == "leisure" and osm_type in ("park", "garden"):
        return "park", "Parc"

    if category == "amenity" and osm_type in ("restaurant", "cafe", "bar", "fast_food"):
        return "food", "Restaurant"

    if category == "shop":
        return "shop", "Commerce"

    if category == "railway":
        return "station", "Gare / station"

    if category == "place":
        return "district", "Quartier / ville"

    return "place", "Lieu"


@app.on_event("startup")
def charger_couleurs_locales():
    print("Lecture de la base de données IDFM locale...")

    if not FICHIER_LIGNES.exists():
        print(f"ERREUR : Fichier JSON introuvable dans {FICHIER_LIGNES}")
        return

    try:
        with open(FICHIER_LIGNES, "r", encoding="utf-8") as f:
            donnees = json.load(f)

        liste_lignes = donnees if isinstance(donnees, list) else donnees.get("results", [])

        for ligne in liste_lignes:
            props = ligne if "transportmode" in ligne else ligne.get("fields", ligne.get("properties", {}))

            mode_brut = str(props.get("transportmode", "")).upper()
            nom = str(props.get("name_line", "")).upper()
            couleur = str(props.get("colourweb_hexa", ""))

            if mode_brut and nom and couleur:
                mode = "BUS"

                if "METRO" in mode_brut or "MÉTRO" in mode_brut:
                    mode = "METRO"
                elif "RER" in mode_brut or "TRAIN" in mode_brut:
                    mode = "RER"
                elif "TRAM" in mode_brut:
                    mode = "TRAM"

                DICTIONNAIRE_COULEURS[f"{mode}_{nom}"] = f"#{couleur.replace('#', '')}"

        print(f"BINGO : {len(DICTIONNAIRE_COULEURS)} couleurs chargées avec succès !")

    except Exception as e:
        print(f"Erreur de lecture du JSON : {e}")


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/api/couleurs")
def obtenir_couleurs():
    return DICTIONNAIRE_COULEURS


@app.get("/api/autocomplete")
def autocomplete(q: str):
    resultats = []

    if not q or len(q.strip()) < 2:
        return {"features": []}

    q = q.strip()
    q_api = nettoyer_requete_utilisateur(q)

    recherche_adresse = contient_numero_adresse(q_api)
    recherche_gare = semble_recherche_gare(q_api)
    recherche_lieu = semble_recherche_lieu(q_api)

    try:
        res_ban = requests.get(
            "https://api-adresse.data.gouv.fr/search/",
            params={"q": q_api, "limit": 10, "lat": "48.8566", "lon": "2.3522"},
            timeout=5
        )

        if res_ban.status_code == 200:
            for feature in res_ban.json().get("features", []):
                props = feature.get("properties", {})
                geometry = feature.get("geometry", {})
                coordinates = geometry.get("coordinates", [])

                if len(coordinates) < 2:
                    continue

                cp = str(props.get("postcode", ""))

                if not cp.startswith(("75", "77", "78", "91", "92", "93", "94", "95")):
                    continue

                title = props.get("name", q_api)
                city = props.get("city", "")
                label = props.get("label", title)
                subtitle = f"{cp} {city}".strip()
                boost = 55 if recherche_adresse else 22

                ajouter_resultat_unique(resultats, {
                    "title": title,
                    "subtitle": subtitle,
                    "detail": label,
                    "type": "address",
                    "type_label": "Adresse",
                    "icon": "",
                    "_query_filtre": q_api,
                    "lon": coordinates[0],
                    "lat": coordinates[1],
                    "score": score_texte(q_api, label) + boost
                })

    except Exception as e:
        print(f"Erreur autocomplete BAN : {e}")

    try:
        res_osm = requests.get(
            "https://nominatim.openstreetmap.org/search",
            headers={"User-Agent": "Citymapper-IDF-Pro/1.0"},
            params={
                "q": q_api,
                "format": "jsonv2",
                "addressdetails": 1,
                "extratags": 1,
                "limit": 14,
                "countrycodes": "fr",
                "viewbox": "1.446,49.241,3.559,48.120",
                "bounded": 1
            },
            timeout=6
        )

        if res_osm.status_code == 200:
            for place in res_osm.json():
                lat = place.get("lat")
                lon = place.get("lon")

                if lat is None or lon is None:
                    continue

                display_name = place.get("display_name", "")
                name = place.get("name") or display_name.split(",")[0]
                category = place.get("category", "")
                osm_type = place.get("type", "")
                address = place.get("address", {})
                extratags = place.get("extratags", {})

                city = (
                    address.get("city")
                    or address.get("town")
                    or address.get("village")
                    or address.get("municipality")
                    or address.get("county")
                    or "Île-de-France"
                )

                postcode = address.get("postcode", "")
                subtitle = f"{postcode} {city}".strip()
                item_type, type_label = type_osm_et_libelle(category, osm_type, extratags)

                boost = 38 if recherche_lieu else 18

                if item_type in ("monument", "health", "park", "district"):
                    boost += 8

                ajouter_resultat_unique(resultats, {
                    "title": name,
                    "subtitle": subtitle,
                    "detail": display_name,
                    "type": item_type,
                    "type_label": type_label,
                    "icon": "",
                    "_query_filtre": q_api,
                    "lon": float(lon),
                    "lat": float(lat),
                    "score": score_texte(q_api, name) + boost
                })

    except Exception as e:
        print(f"Erreur autocomplete Nominatim : {e}")

    try:
        res_nav = requests.get(
            "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/places",
            headers={"apiKey": API_KEY},
            params={"q": q_api, "count": 10, "type[]": ["stop_area"]},
            timeout=5
        )

        if res_nav.status_code == 200:
            for place in res_nav.json().get("places", []):
                emb = place.get("embedded_type")

                if not emb or emb not in place:
                    continue

                coord = place[emb].get("coord")
                name = place.get("name")

                if not coord or not name:
                    continue

                subtitle = "Île-de-France"
                admin = place[emb].get("administrative_regions", [])

                if admin:
                    subtitle = admin[0].get("name", "Île-de-France")

                boost = 45 if recherche_gare else 10

                ajouter_resultat_unique(resultats, {
                    "title": name,
                    "subtitle": subtitle,
                    "detail": f"Gare / station · {subtitle}",
                    "type": "station",
                    "type_label": "Gare / station",
                    "icon": "🚆",
                    "_query_filtre": q_api,
                    "lon": coord.get("lon"),
                    "lat": coord.get("lat"),
                    "score": score_texte(q_api, name) + boost
                })

    except Exception as e:
        print(f"Erreur autocomplete Navitia : {e}")

    resultats = sorted(resultats, key=lambda x: x.get("score", 0), reverse=True)

    for item in resultats:
        item.pop("score", None)

    return {"features": resultats[:12]}


@app.get("/api/reverse")
def reverse_geocode(lat: float, lon: float):
    try:
        res = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            headers={"User-Agent": "Citymapper-IDF-Pro/1.0"},
            params={"lat": lat, "lon": lon, "format": "jsonv2", "addressdetails": 1, "zoom": 18},
            timeout=6
        )

        if res.status_code != 200:
            return {"title": "Position sélectionnée", "subtitle": "Île-de-France", "type": "location", "type_label": "Position", "icon": "", "lat": lat, "lon": lon}

        data = res.json()
        address = data.get("address", {})

        title = (
            data.get("name")
            or address.get("amenity")
            or address.get("tourism")
            or address.get("road")
            or address.get("pedestrian")
            or address.get("suburb")
            or "Position sélectionnée"
        )

        house_number = address.get("house_number")
        road = address.get("road")

        if house_number and road:
            title = f"{house_number} {road}"

        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or address.get("suburb")
            or "Île-de-France"
        )

        postcode = address.get("postcode", "")
        subtitle = f"{postcode} {city}".strip()

        return {"title": title, "subtitle": subtitle, "type": "location", "type_label": "Position", "icon": "", "lat": lat, "lon": lon}

    except Exception as e:
        print(f"Erreur reverse geocode : {e}")
        return {"title": "Position sélectionnée", "subtitle": "Île-de-France", "type": "location", "type_label": "Position", "icon": "", "lat": lat, "lon": lon}


@app.get("/api/pois")
def obtenir_pois(
    south: float = Query(...),
    west: float = Query(...),
    north: float = Query(...),
    east: float = Query(...)
):
    overpass_url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json][timeout:12];
    (
      node["amenity"="hospital"]({south},{west},{north},{east});
      way["amenity"="hospital"]({south},{west},{north},{east});

      node["amenity"="clinic"]({south},{west},{north},{east});
      way["amenity"="clinic"]({south},{west},{north},{east});

      node["amenity"="pharmacy"]({south},{west},{north},{east});
      way["amenity"="pharmacy"]({south},{west},{north},{east});

      node["tourism"="museum"]({south},{west},{north},{east});
      way["tourism"="museum"]({south},{west},{north},{east});

      node["tourism"="attraction"]({south},{west},{north},{east});
      way["tourism"="attraction"]({south},{west},{north},{east});

      node["historic"="monument"]({south},{west},{north},{east});
      way["historic"="monument"]({south},{west},{north},{east});

      node["historic"="memorial"]({south},{west},{north},{east});
      way["historic"="memorial"]({south},{west},{north},{east});
    );
    out center tags 150;
    """

    try:
        response = requests.post(overpass_url, data={"data": query}, timeout=15)

        if response.status_code != 200:
            return {"features": []}

        features = []

        for element in response.json().get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name")

            if not name:
                continue

            lat = element.get("lat")
            lon = element.get("lon")

            if lat is None or lon is None:
                center = element.get("center", {})
                lat = center.get("lat")
                lon = center.get("lon")

            if lat is None or lon is None:
                continue

            category = "place"
            type_label = "Lieu"

            if tags.get("amenity") in ("hospital", "clinic"):
                category = "health"
                type_label = "Santé"
            elif tags.get("amenity") == "pharmacy":
                category = "health"
                type_label = "Pharmacie"
            elif tags.get("tourism") == "museum":
                category = "museum"
                type_label = "Musée"
            elif tags.get("tourism") == "attraction" or tags.get("historic") in ("monument", "memorial"):
                category = "monument"
                type_label = "Lieu culturel"

            features.append({
                "title": name,
                "subtitle": type_label,
                "type": category,
                "type_label": type_label,
                "icon": "",
                "lat": lat,
                "lon": lon
            })

        return {"features": features[:120]}

    except Exception as e:
        print(f"Erreur POI Overpass : {e}")
        return {"features": []}


@app.get("/api/trajet")
def calculer_trajet(
    lon_dep: str,
    lat_dep: str,
    lon_arr: str,
    lat_arr: str,
    datetime: str,
    heure_type: str
):
    url = "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/journeys"
    navitia_datetime_represents = "arrival" if heure_type == "arrivée" else "departure"

    params = {
        "from": f"{lon_dep};{lat_dep}",
        "to": f"{lon_arr};{lat_arr}",
        "datetime": datetime,
        "datetime_represents": navitia_datetime_represents,
        "max_nb_journeys": 7
    }

    try:
        reponse = requests.get(url, headers=IDFM_HEADERS, params=params, timeout=20)

        if reponse.status_code == 200:
            return reponse.json()

        print("Erreur IDFM :", reponse.status_code, reponse.text[:500])
        raise HTTPException(status_code=reponse.status_code, detail="Erreur IDFM")

    except HTTPException:
        raise

    except Exception as e:
        print(f"Erreur réseau trajet : {e}")
        raise HTTPException(status_code=500, detail="Erreur réseau")
