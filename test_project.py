from pathlib import Path
import subprocess
import sys

print("TEST PRODUCTION CITYMAPPER IDF")
print("=" * 60)

for file in ["main.py", "index.html", "requirements.txt", ".env.example"]:
    print(file, ":", "OK" if Path(file).exists() else "MANQUANT")

result = subprocess.run(
    [sys.executable, "-m", "py_compile", "main.py"],
    capture_output=True,
    text=True
)

print("Syntaxe main.py :", "OK" if result.returncode == 0 else "ERREUR")
if result.returncode != 0:
    print(result.stderr)

html = Path("index.html").read_text(encoding="utf-8", errors="ignore")
print("HTML complet :", "OK" if "</html>" in html else "ERREUR")
print("Carte :", "OK" if 'id="map"' in html else "MANQUANT")
print("Autocomplete :", "OK" if "/api/autocomplete" in html else "MANQUANT")
print("Correspondances :", "OK" if "correspondance(s)" in html else "MANQUANT")
print("Marche :", "OK" if "min marche" in html else "MANQUANT")

try:
    import main
    print("Import FastAPI :", "OK")
    print("App :", "OK" if hasattr(main, "app") else "MANQUANTE")
except Exception as e:
    print("Import FastAPI : ERREUR")
    print(e)

print("=" * 60)
print("TEST TERMINÉ")
