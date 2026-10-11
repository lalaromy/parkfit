# parkfit — a multi-source data fusion engine for vehicle-specific parking suitability

![ci](https://github.com/lalaromy/parkfit/actions/workflows/ci.yml/badge.svg)

MSc Computer Science final project, University of London. Author: Romy Abbrederis.
Repository: https://github.com/lalaromy/parkfit

**Question answered:** *"Can my 2.05 m high van park here?"* — for any point in the study
area (Zurich inner city), by fusing OpenStreetMap, City of Zurich open data and
operator-published facility pages into one explainable, confidence-scored answer, and
evaluating it against a purpose-built field-survey ground truth.

## What is in the box

| Layer | Module | Proposal objective |
|---|---|---|
| Ingestion into a canonical schema (raw responses cached in `data/raw/`) | `parkfit/ingest/` | 2 |
| Staged feature matcher (spatial buffer → name similarity → ambiguity check) | `parkfit/matching/` | 2 |
| Fusion: confidence-weighted voting **and** simplified Dempster–Shafer, intrinsic OSM quality signals, contextual inference for missing attributes | `parkfit/fusion/` | 3 |
| Query API with evidence chain + Leaflet demo page | `parkfit/api/` | 4 |
| Ground-truth dataset, protocol and schema | `data/ground_truth/`, `docs/ground_truth_protocol.md` | 5 |
| Evaluation vs single-source baselines across 5 vehicle profiles, error taxonomy, figures | `parkfit/evaluation/` | 6 |
| Storage: SQLite (zero setup) or PostGIS (docker compose) | `parkfit/storage/` | 2 |

## Quick start (hello world in five commands)

```bash
git clone https://github.com/lalaromy/parkfit.git
cd parkfit
uv venv .venv && uv pip install -e ".[dev]"      # or: python -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest                        # 24 unit/integration tests, no network needed
.venv/bin/parkfit run                             # ingest (cached) -> match -> fuse -> SQLite
.venv/bin/parkfit evaluate                        # writes reports/results.md + figures
.venv/bin/parkfit serve                           # http://127.0.0.1:8000  (demo map)  /docs (OpenAPI)
```

Ask the engine from the shell:

```bash
.venv/bin/parkfit query 47.3745 8.5405 1.99 --width 1.90 --radius 400
```

`data/raw/` ships with the OpenStreetMap, Zurich register and operator-page snapshots used
for the reported results, so everything above runs offline. The Google Places snapshot is
**not** in the repository (Google's terms restrict redistribution); without it the
evaluation reproduces the OSM, register and operator configurations, which give the same
classification results as the four-source configuration on the surveyed facilities. Add
`--force` to `parkfit run` to re-fetch live data.

### Optional pieces

* **PostGIS backend** (the proposal's spatial store):
  `docker compose up -d`, then prefix commands with
  `DATABASE_URL=postgresql+psycopg://parkfit:parkfit@localhost:5433/parkfit`.
  Radius queries then use `ST_DWithin` on a GiST-indexed geography column.
* **Google Places** (fourth source): the archived snapshot in `data/raw/places/` is used
  offline without a key. To re-fetch, put `GOOGLE_PLACES_API_KEY=...` in `.env` (copy
  `.env.example`) and run `parkfit run --force`.

## Sources

| source | what it gives | licence | height? |
|---|---|---|---|
| OpenStreetMap via Overpass (`out meta` for version/timestamp) | `maxheight`, `capacity`, `parking=*`, name | ODbL | sometimes |
| City of Zurich OGD *Öffentlich zugängliche Parkhäuser* (WFS) | authoritative register: name, address, capacity breakdown | CC0 | no |
| Zurich Parkleitsystem operator pages (pls-zh.ch) | `Einfahrthöhe`, capacity, address for PLS-connected garages | CC0 | yes |
| Google Places (optional) | name, type, location | Google ToS (no caching of restricted fields) | no |

## Repository layout

```
parkfit/            package (see table above)
data/ground_truth/  zurich_garages_2026.csv  — 23 field-surveyed garages, 3 survey days
data/raw/           cached source snapshots (reproducibility)
data/processed/     records.json, groups.json, fused_features.json, parkfit.sqlite
reports/            results.md, results.json, figures/
docs/               ground_truth_protocol.md, data_schema.md, matching_calibration.md, design_decisions.md
tests/              pytest suite
```

## Continuous integration

`.github/workflows/ci.yml` runs Ruff, the test suite and the offline evaluation on every push.

## Reproducing the reported numbers

`parkfit evaluate` recomputes every table in `reports/results.md` from `data/raw/` and
`data/ground_truth/`. Each configuration runs matching, fusion and inference on its own
sources only; ground-truth facilities are joined to fused features by hand-verified record
identifiers (`expected_*_id` columns), never by proximity, with an explicit *unmatched*
outcome. Dependencies are pinned to exact versions in `pyproject.toml`.

## Ethics and licensing

Code is MIT-licensed; the ground-truth survey is CC BY 4.0; see `LICENSE` for the data
licences. Only public data is used, under ODbL (attribution: © OpenStreetMap contributors),
CC0 (Stadt Zürich) and the Google Places terms. The ground truth was collected from publicly
accessible streets and garage entrances; no people are recorded. See
`docs/ground_truth_protocol.md`.
