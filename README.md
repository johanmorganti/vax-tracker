# VaxTracker

A small Flask website that tracks childhood vaccine schedules across countries, and helps you understand what your child may still need when relocating.

No login. No database. Just JSON data files and Python.

## Features

- Browse mandatory and recommended vaccine schedules by country
- See doses grouped by age, with the actual vaccine products used
- **Relocation tool**: select two countries and your child's age — get a list of what's already covered and what's still missing, with primary doses and boosters shown separately

## Running locally

```bash
pip install flask
python app.py
```

Then open `http://localhost:5001`.

## Running tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Adding a country

1. Add an entry to `data/countries/_index.json`:
   ```json
   {"code": "de", "name": "Germany", "flag": "🇩🇪", "region": "Europe"}
   ```

2. Create `data/countries/de.json` following the same structure as an existing country file. Key fields per dose:
   - `ageMonths` — integer, used for all comparisons
   - `antigens` — list of antigen IDs from `data/antigens.json` (denormalized onto each dose)
   - `doseType` — `"primary"` or `"booster"`
   - `status` — `"mandatory"` or `"recommended"`

3. Add any new vaccine products to `data/products.json` if needed.

That's it — no code changes required.

## Project structure

```
data/
  antigens.json          # master list of disease targets
  products.json          # vaccine brand catalogue
  countries/
    _index.json          # country list for navigation
    fr.json              # one file per country
    kr.json
    sg.json

app/
  __init__.py            # Flask app factory
  routes.py              # URL routes
  lib/
    data.py              # JSON loaders
    equivalency.py       # cross-country matching engine

templates/
  base.html
  index.html             # country picker
  schedule.html          # single-country schedule view
  compare.html           # relocation comparison tool

tests/
  test_equivalency.py
```

## Data model notes

The equivalency engine matches by **antigen ID** — the actual disease target — not by brand or combination product. A child who received Infanrix Hexa (DTaP-IPV-Hib-HepB) in France counts as having received `ipv`, which satisfies South Korea's polio requirement even if Korea uses a different product.

Primary doses and booster doses are tracked with separate deficits, so a child whose primary series transferred from country A will correctly show only the boosters as still needed in country B — not the primary doses.

## Disclaimer

This tool is for informational purposes only. Vaccine schedules change. Always verify with your doctor or local health authority before making any vaccination decisions.
