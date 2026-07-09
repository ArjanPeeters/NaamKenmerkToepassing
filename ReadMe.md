This is the Repo for the Naa.K.T. site a dutch initiative for Material names in BIM
You can find more info about it [here](https://www.bimloket.nl/p/682/1-NAAKT-Eenduidige-materiaalbenaming)

De site is een **statische** app: geen server, geen database at runtime. Alle
referentiedata staat in `static/data.json` en alle logica draait in de browser.
Opgeslagen materiaallijsten leven in `localStorage`.

# Requirements
- Node.js 18+ (voor de build)
- Python 3.10 (alleen voor het bijwerken van de data, zie hieronder)

# Build
- `npm i`
- `npm run prod`  (bouwt `static/scripts.js` + `static/style.css`)

# Lokaal draaien
- `python -m http.server 8000` en open http://localhost:8000
  (elke statische webserver volstaat; open index.html niet via file:// i.v.m. fetch)

# Data bijwerken
De data komt uit de Excel-lijst. Dit is een lokale stap:
1. `pip install -r requirements.txt`
2. `python import_excel.py "pad\naar\lijst vX.xlsm"`  -> vult de SQLite DB
3. `python dump_json.py`  -> schrijft `static/data.json`
4. commit `static/data.json` en push

# Deploy (GitHub Pages)
Push naar de branch die Pages serveert; de site is puur statisch
(`index.html`, `static/`, `.nojekyll`). Geen Cloud Run / Docker meer nodig.
