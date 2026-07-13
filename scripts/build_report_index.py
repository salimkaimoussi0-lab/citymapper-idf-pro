from pathlib import Path
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CARTES = REPORTS / "cartes"
HTML_TABLES = REPORTS / "html_tables"
OUT = REPORTS / "rapport_colab_style.html"

CARTES.mkdir(parents=True, exist_ok=True)
HTML_TABLES.mkdir(parents=True, exist_ok=True)

cartes = sorted(CARTES.glob("*.html"))
tables = sorted(HTML_TABLES.glob("*.html"))

def rel(path):
    return path.resolve().relative_to(REPORTS.resolve()).as_posix()

sections = ""

for carte in cartes:
    sections += f"""
<section class="card">
  <h2>Carte / graphique : {carte.name}</h2>
  <iframe src="{rel(carte)}"></iframe>
</section>
"""

for table in tables:
    sections += f"""
<section class="card">
  <h2>Tableau : {table.name}</h2>
  <iframe src="{rel(table)}"></iframe>
</section>
"""

if not sections:
    sections = """
<section class="card">
  <h2>Aucun rapport généré</h2>
  <p>Lance d'abord : bash scripts/run_colab_style_analysis.sh</p>
</section>
"""

html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Rapport Colab Style - Citymapper IDF Pro</title>
<style>
body {{
  margin: 0;
  font-family: Arial, sans-serif;
  background: #f4f7fb;
  color: #111827;
}}
header {{
  background: white;
  padding: 28px 40px;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 10;
}}
h1 {{
  margin: 0;
  font-size: 32px;
}}
.subtitle {{
  color: #64748b;
  margin-top: 8px;
}}
main {{
  padding: 28px 40px;
}}
.card {{
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  padding: 24px;
  margin-bottom: 28px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}}
h2 {{
  margin-top: 0;
}}
iframe {{
  width: 100%;
  height: 780px;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: white;
}}
</style>
</head>
<body>
<header>
  <h1>Rapport Colab Style — Citymapper IDF Pro</h1>
  <div class="subtitle">Cartes dynamiques Plotly + tableaux interactifs filtrables.</div>
</header>
<main>
{sections}
</main>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print("Rapport global généré :", OUT)
webbrowser.open(OUT.resolve().as_uri())
