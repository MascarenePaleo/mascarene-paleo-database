# Mascarene Paleo API

Interactive, read-only access to **Mascarene Paleo Framework database v0.4**, including the canonical specimen tables and the integrated Darwin Core occurrence view.

The repository has two complementary interactive surfaces:

1. **GitHub Pages specimen explorer** — works directly from the `docs/` folder and static JSON snapshots. No server is required.
2. **FastAPI REST API** — provides query parameters, joined record detail, CSV exports, OpenAPI, Swagger UI (`/docs`) and ReDoc (`/redoc`). It must be deployed to a Python-capable host because GitHub Pages cannot execute Python.

## Dataset snapshot

The packaged snapshot is built from:

`data/Mascarene_Palaeo_Core_Database_v0.4_DwC_integrated.xlsx`

Current generated counts:

- 302 specimen records
- 30 taxon records (30 unique taxon IDs)
- 9 localities
- 32 publications
- 10 source records
- 324 record-source links
- 7 unresolved questions
- 302 Darwin Core occurrence rows
- 284 `FossilSpecimen` and 18 `MaterialCitation` Darwin Core records

See `data/build_report.json` for build-time validation notes.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- Explorer: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

## Main endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/stats` | Dataset summary |
| `GET /api/v1/specimens` | Search/filter specimen records |
| `GET /api/v1/specimens/{specimen_id}` | Joined specimen + taxon + locality + sources + DwC record |
| `GET /api/v1/taxa` | Taxon records |
| `GET /api/v1/taxa/{species_id}` | Taxon detail and linked specimens |
| `GET /api/v1/localities` | Locality records |
| `GET /api/v1/publications` | Publications and datasets |
| `GET /api/v1/sources` | Evidence/source register |
| `GET /api/v1/questions` | Explicit unresolved-question register |
| `GET /api/v1/search?q=...` | Cross-table search |
| `GET /api/v1/dwc/occurrences` | Darwin Core occurrence view |
| `GET /api/v1/dwc/mapping` | Canonical-to-Darwin-Core field mapping |
| `GET /api/v1/dwc/qc` | Darwin Core QC summary |
| `GET /api/v1/export/specimens.csv` | Download canonical specimens as CSV |
| `GET /api/v1/export/darwin-core-occurrence.csv` | Download DwC occurrence export as CSV |

### Example queries

```text
/api/v1/specimens?island=Rodrigues
/api/v1/specimens?scientific_name=Pezophaps&photograph_available=Yes
/api/v1/specimens?search=humerus&repository=NHMUK
/api/v1/dwc/occurrences?basis_of_record=MaterialCitation
/api/v1/search?q=Mare%20aux%20Songes
```

Pagination uses `limit` and `offset` where applicable. `limit` is capped at 500 records per request.

## Enable the GitHub Pages explorer

In the GitHub repository:

1. Open **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Select your main branch and the `/docs` folder.
4. Save.

The resulting Pages site will load `docs/data/specimens_joined.json` and provide local search/filtering. It does **not** replace the REST API; it is the serverless public explorer.

## Deploy the REST API

The repository includes both `Dockerfile` and `render.yaml`. Any Python/ASGI host can run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

CORS is read-only and open so a separate public front end can query the API.

## Data model

The API keeps the Mascarene Paleo identifiers intact:

- `MAS-SP-*` — specimens / occurrences
- `MAS-TAX-*` — taxa
- `MAS-LOC-*` — localities
- `MAS-PUB-*` — publications
- `MAS-SRC-*` — sources
- `MAS-Q-*` — unresolved questions
- `MAS-RS-*` — record-source links

`/api/v1/specimens/{id}` performs the principal join, keeping the canonical database fields visible while also returning the corresponding Darwin Core occurrence record when present.

## Data integrity

The packaged v0.4 workbook has been cleaned before API generation. Primary identifiers are unique across the canonical taxa, localities, specimens, publications, sources, unresolved questions, record-source links, and Darwin Core occurrence view. The API therefore serves the canonical source rows directly and does not apply runtime taxon deduplication. `data/build_report.json` records the current primary-key, DOI-duplication, and relationship checks.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

GitHub Actions runs the same validation on pushes and pull requests.

## Versioning

API paths are versioned under `/api/v1/`. Dataset version is reported separately by `/health` and `/api/v1/stats`, so future database freezes can advance without silently changing the API contract.

### Character encoding

API JSON responses explicitly declare UTF-8, and CSV exports include a UTF-8 BOM so accented names and punctuation (for example `Gônet`, `Günther`, `André`, `·`, and `–`) render correctly in browsers and spreadsheet software.

