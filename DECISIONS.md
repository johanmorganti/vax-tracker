# Architecture & Design Decisions

Decisions made during initial design and build of VaxTracker.

---

## Tech stack

- **Flask** (Python) — chosen over Next.js/TypeScript at user's preference for a Python-oriented stack
- **Jinja2** — templating, built into Flask
- **Tailwind CSS via CDN** — no build step, sufficient for a personal project
- **No database** — vaccine schedules change infrequently (~once/year per country); JSON files in the repo are simpler to maintain, diff, and audit
- **No authentication** — the site is intentionally public and identical for all users
- **Deployment** — Docker container on a self-hosted server (not yet implemented)

## Data model

Three-layer separation:

1. **`data/antigens.json`** — master registry of disease targets (e.g. `ipv`, `dtx`, `hib`)
2. **`data/products.json`** — vaccine brand catalogue; each product lists which antigen IDs it covers
3. **`data/countries/<code>.json`** — one file per country; each dose entry references products and has antigens **denormalized** directly onto it

Key decisions within the model:

- **Antigen ID is the unit of equivalency** — a child who received Infanrix Hexa (DTaP-IPV-Hib-HepB) in France counts as having `ipv`, which satisfies Korea's polio requirement regardless of the product used there
- **Antigens denormalized onto each dose** — avoids joins at runtime; makes the equivalency engine a simple loop
- **`ageMonths` as integer** — canonical numeric field used for all comparisons; `ageLabel` is display-only
- **One JSON file per country** — keeps pull requests focused; a schedule update touches exactly one file
- **`region` field on each country** — added to `_index.json` to support grouped display as the country list grows

## Equivalency engine

- Lives in `app/lib/equivalency.py` as a pure function with no side effects
- Assumes the child received **all** doses scheduled in country A up to their current age (no per-dose tracking in v1)
- Does not validate minimum intervals between doses (v1 scope decision — flag for future)
- HPV dose count edge case (2 vs 3 doses depending on age) is not modelled; deferred to a "consult doctor" note

## UI

- **Region grouping + live search** on the index page — flat grid doesn't scale past ~15 countries
- Search filters cards and hides empty region headers client-side with vanilla JS (no framework)
- Country grid: 5 columns on large screens, smaller cards (compact for many countries)
- Covered doses on the compare results page are collapsed by default (`<details>`) to keep focus on what's missing

## Pilot countries

France, South Korea, Singapore — chosen by the user to reflect actual relocation history.
Notable cross-country differences captured:
- Korea adds **JEV** (Japanese Encephalitis) and **HepA** — always flagged as missing for children coming from France or Singapore
- France's **hexavalent** (DTaP-IPV-Hib-HepB) correctly satisfies Singapore's **pentavalent** (DTaP-IPV-Hib) series via antigen matching
- France added **Varicella** to its mandatory schedule in January 2024
- Singapore's legal compulsion covers only Diphtheria and Measles; all other NCIP vaccines are marked `mandatory` in the data for practical purposes
