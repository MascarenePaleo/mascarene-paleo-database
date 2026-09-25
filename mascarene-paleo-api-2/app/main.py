from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

from .db import ROOT, connect, rows_to_dicts

APP_VERSION = "0.4.0"
DATASET_VERSION = "0.4"

app = FastAPI(
    title="Mascarene Paleo API",
    version=APP_VERSION,
    summary="Queryable access to the Mascarene Paleo Framework database",
    description=(
        "Read-only API for specimens, taxa, localities, publications, sources, "
        "unresolved questions, and the Darwin Core occurrence view of the Mascarene Paleo dataset."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.middleware("http")
async def explicit_utf8_for_json(request, call_next):
    """Make browser rendering of raw JSON unambiguous.

    JSON is UTF-8 by specification, but some browser/raw-response views can
    mis-detect non-ASCII characters when no charset parameter is present.
    """
    response = await call_next(request)
    content_type = response.headers.get("content-type", "")
    if content_type.lower().startswith("application/json") and "charset=" not in content_type.lower():
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response


def _paged(items: list[dict], limit: int, offset: int, total: int) -> dict:
    return {"total": total, "limit": limit, "offset": offset, "items": items}


def _fetch_one(sql: str, params: list[Any]) -> dict:
    with connect() as con:
        row = con.execute(sql, params).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return dict(row)


def _table_export(table: str, filename: str):
    with connect() as con:
        rows = con.execute(f'SELECT * FROM "{table}"').fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No rows available")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows([dict(r) for r in rows])
    output.seek(0)
    # UTF-8 BOM helps Excel and other spreadsheet apps preserve accents.
    csv_text = "\ufeff" + output.getvalue()
    return StreamingResponse(
        iter([csv_text]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/", include_in_schema=False)
def home() -> HTMLResponse:
    index = ROOT / "docs" / "index.html"
    if index.exists():
        return HTMLResponse(index.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Mascarene Paleo API</h1><p>See <a href='/docs'>/docs</a>.</p>")


@app.get("/health", tags=["Meta"])
def health() -> dict:
    return {"status": "ok", "api_version": APP_VERSION, "dataset_version": DATASET_VERSION}


@app.get("/api/v1/stats", tags=["Meta"])
def stats() -> dict:
    path = ROOT / "data" / "stats.json"
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/v1/build-report", tags=["Meta"])
def build_report() -> dict:
    path = ROOT / "data" / "build_report.json"
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/v1/specimens", tags=["Specimens"])
def list_specimens(
    search: str | None = None,
    taxon_id: str | None = None,
    scientific_name: str | None = None,
    island: str | None = None,
    repository: str | None = None,
    locality: str | None = None,
    evidence_confidence: str | None = None,
    record_provenance_class: str | None = None,
    photograph_available: Literal["Yes", "No"] | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    where: list[str] = []
    params: list[Any] = []

    if search:
        term = f"%{search}%"
        where.append("(s.specimen_id LIKE ? OR s.catalogue_number LIKE ? OR s.element LIKE ? OR s.provenance LIKE ? OR s.notes LIKE ? OR t.accepted_name LIKE ? OR l.locality_name LIKE ?)")
        params.extend([term] * 7)
    if taxon_id:
        where.append("s.species_id = ?")
        params.append(taxon_id)
    if scientific_name:
        where.append("t.accepted_name LIKE ?")
        params.append(f"%{scientific_name}%")
    if island:
        where.append("COALESCE(l.island, t.island) = ?")
        params.append(island)
    if repository:
        where.append("s.repository LIKE ?")
        params.append(f"%{repository}%")
    if locality:
        where.append("l.locality_name LIKE ?")
        params.append(f"%{locality}%")
    if evidence_confidence:
        where.append("s.evidence_confidence = ?")
        params.append(evidence_confidence)
    if record_provenance_class:
        where.append("s.record_provenance_class = ?")
        params.append(record_provenance_class)
    if photograph_available:
        where.append("s.photograph_available = ?")
        params.append(photograph_available)

    clause = " WHERE " + " AND ".join(where) if where else ""
    select = """
        SELECT s.*, t.accepted_name AS scientific_name, t.authority,
               l.locality_name, COALESCE(l.island, t.island) AS island,
               l.latitude, l.longitude
        FROM specimens s
        LEFT JOIN taxa t ON t.species_id = s.species_id
        LEFT JOIN localities l ON l.locality_id = s.locality_id
    """
    with connect() as con:
        total = con.execute(
            "SELECT COUNT(*) FROM specimens s LEFT JOIN taxa t ON t.species_id=s.species_id LEFT JOIN localities l ON l.locality_id=s.locality_id" + clause,
            params,
        ).fetchone()[0]
        rows = con.execute(select + clause + " ORDER BY s.specimen_id LIMIT ? OFFSET ?", [*params, limit, offset]).fetchall()
    return _paged(rows_to_dicts(rows), limit, offset, total)


@app.get("/api/v1/specimens/{specimen_id}", tags=["Specimens"])
def get_specimen(specimen_id: str) -> dict:
    specimen = _fetch_one(
        """
        SELECT s.*, t.accepted_name AS scientific_name, t.authority, t.synonyms,
               t.[group] AS taxon_group, t.extinction_status,
               l.locality_name, l.island, l.latitude, l.longitude,
               l.age AS locality_age, l.stratigraphic_information
        FROM specimens s
        LEFT JOIN taxa t ON t.species_id = s.species_id
        LEFT JOIN localities l ON l.locality_id = s.locality_id
        WHERE s.specimen_id = ?
        """,
        [specimen_id],
    )
    with connect() as con:
        source_rows = con.execute(
            """
            SELECT src.*, rs.relationship, rs.notes AS link_notes
            FROM record_sources rs
            JOIN sources src ON src.source_id = rs.source_id
            WHERE rs.record_id = ? ORDER BY src.source_id
            """,
            [specimen_id],
        ).fetchall()
        dwc = con.execute("SELECT * FROM darwin_core_occurrence WHERE occurrenceID = ?", [specimen_id]).fetchone()
    specimen["sources"] = rows_to_dicts(source_rows)
    specimen["darwin_core"] = dict(dwc) if dwc else None
    if specimen["darwin_core"] and specimen["darwin_core"].get("dynamicProperties"):
        try:
            specimen["darwin_core"]["dynamicProperties"] = json.loads(specimen["darwin_core"]["dynamicProperties"])
        except json.JSONDecodeError:
            pass
    return specimen


@app.get("/api/v1/taxa", tags=["Taxa"])
def list_taxa(
    search: str | None = None,
    island: str | None = None,
    extinction_status: str | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    where=[]; params=[]
    if search:
        where.append("(accepted_name LIKE ? OR original_name LIKE ? OR synonyms LIKE ? OR notes LIKE ?)")
        params.extend([f"%{search}%"]*4)
    if island:
        where.append("island = ?"); params.append(island)
    if extinction_status:
        where.append("extinction_status = ?"); params.append(extinction_status)
    clause=" WHERE "+" AND ".join(where) if where else ""
    with connect() as con:
        total=con.execute("SELECT COUNT(*) FROM taxa"+clause,params).fetchone()[0]
        rows=con.execute("SELECT * FROM taxa"+clause+" ORDER BY accepted_name LIMIT ? OFFSET ?",[*params,limit,offset]).fetchall()
    return _paged(rows_to_dicts(rows),limit,offset,total)


@app.get("/api/v1/taxa/{species_id}", tags=["Taxa"])
def get_taxon(species_id: str) -> dict:
    taxon=_fetch_one("SELECT * FROM taxa WHERE species_id = ?",[species_id])
    with connect() as con:
        taxon["specimen_count"] = con.execute("SELECT COUNT(*) FROM specimens WHERE species_id = ?",[species_id]).fetchone()[0]
        taxon["specimen_ids"] = [r[0] for r in con.execute("SELECT specimen_id FROM specimens WHERE species_id = ? ORDER BY specimen_id",[species_id]).fetchall()]
    return taxon


@app.get("/api/v1/localities", tags=["Localities"])
def list_localities(search: str | None = None, island: str | None = None) -> list[dict]:
    where=[]; params=[]
    if search:
        where.append("(locality_name LIKE ? OR notes LIKE ? OR stratigraphic_information LIKE ?)")
        params.extend([f"%{search}%"]*3)
    if island:
        where.append("island = ?"); params.append(island)
    clause=" WHERE "+" AND ".join(where) if where else ""
    with connect() as con:
        rows=con.execute("SELECT * FROM localities"+clause+" ORDER BY island, locality_name",params).fetchall()
    return rows_to_dicts(rows)


@app.get("/api/v1/localities/{locality_id}", tags=["Localities"])
def get_locality(locality_id: str) -> dict:
    locality=_fetch_one("SELECT * FROM localities WHERE locality_id = ?",[locality_id])
    with connect() as con:
        locality["specimen_count"] = con.execute("SELECT COUNT(*) FROM specimens WHERE locality_id = ?",[locality_id]).fetchone()[0]
    return locality


@app.get("/api/v1/publications", tags=["Publications"])
def list_publications(
    search: str | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    where=[]; params=[]
    if search:
        where.append("(citation LIKE ? OR species LIKE ? OR localities LIKE ? OR contribution LIKE ?)")
        params.extend([f"%{search}%"]*4)
    if year_min is not None:
        where.append("CAST(year AS INTEGER) >= ?"); params.append(year_min)
    if year_max is not None:
        where.append("CAST(year AS INTEGER) <= ?"); params.append(year_max)
    clause=" WHERE "+" AND ".join(where) if where else ""
    with connect() as con:
        total=con.execute("SELECT COUNT(*) FROM publications"+clause,params).fetchone()[0]
        rows=con.execute("SELECT * FROM publications"+clause+" ORDER BY CAST(year AS INTEGER) DESC, publication_id LIMIT ? OFFSET ?",[*params,limit,offset]).fetchall()
    return _paged(rows_to_dicts(rows),limit,offset,total)


@app.get("/api/v1/sources", tags=["Sources"])
def list_sources(search: str | None = None) -> list[dict]:
    params=[]; clause=""
    if search:
        clause=" WHERE source_label LIKE ? OR notes LIKE ? OR applies_to LIKE ?"
        params=[f"%{search}%"]*3
    with connect() as con:
        rows=con.execute("SELECT * FROM sources"+clause+" ORDER BY source_id",params).fetchall()
    return rows_to_dicts(rows)


@app.get("/api/v1/questions", tags=["Unresolved questions"])
def list_questions(status: str | None = None, priority: str | None = None, category: str | None = None) -> list[dict]:
    where=[]; params=[]
    if status: where.append("status = ?"); params.append(status)
    if priority: where.append("priority = ?"); params.append(priority)
    if category: where.append("category = ?"); params.append(category)
    clause=" WHERE "+" AND ".join(where) if where else ""
    with connect() as con:
        rows=con.execute("SELECT * FROM unresolved_questions"+clause+" ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, question_id",params).fetchall()
    return rows_to_dicts(rows)


@app.get("/api/v1/dwc/occurrences", tags=["Darwin Core"])
def list_dwc_occurrences(
    search: str | None = None,
    taxon_id: str | None = None,
    scientific_name: str | None = None,
    island: str | None = None,
    institution_code: str | None = None,
    basis_of_record: str | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    where=[]; params=[]
    if search:
        where.append("(occurrenceID LIKE ? OR catalogNumber LIKE ? OR scientificName LIKE ? OR locality LIKE ? OR materialEntityType LIKE ? OR occurrenceRemarks LIKE ?)")
        params.extend([f"%{search}%"]*6)
    filters=[("taxonID",taxon_id),("scientificName",scientific_name),("island",island),("institutionCode",institution_code),("basisOfRecord",basis_of_record)]
    for col,val in filters:
        if val:
            op="LIKE" if col=="scientificName" else "="
            where.append(f'"{col}" {op} ?')
            params.append(f"%{val}%" if op=="LIKE" else val)
    clause=" WHERE "+" AND ".join(where) if where else ""
    with connect() as con:
        total=con.execute("SELECT COUNT(*) FROM darwin_core_occurrence"+clause,params).fetchone()[0]
        rows=rows_to_dicts(con.execute("SELECT * FROM darwin_core_occurrence"+clause+" ORDER BY occurrenceID LIMIT ? OFFSET ?",[*params,limit,offset]).fetchall())
    for row in rows:
        if row.get("dynamicProperties"):
            try: row["dynamicProperties"] = json.loads(row["dynamicProperties"])
            except json.JSONDecodeError: pass
    return _paged(rows,limit,offset,total)


@app.get("/api/v1/dwc/mapping", tags=["Darwin Core"])
def list_dwc_mapping() -> list[dict]:
    with connect() as con:
        rows=con.execute("SELECT * FROM dwc_mapping").fetchall()
    return rows_to_dicts(rows)


@app.get("/api/v1/dwc/qc", tags=["Darwin Core"])
def list_dwc_qc() -> list[dict]:
    with connect() as con:
        rows=con.execute("SELECT * FROM dwc_qc").fetchall()
    return rows_to_dicts(rows)


@app.get("/api/v1/search", tags=["Search"])
def search_all(
    q: Annotated[str, Query(min_length=2, max_length=120)],
    entity_type: Literal["specimen", "taxon", "locality", "publication", "question"] | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
) -> dict:
    term=f"%{q}%"
    params: list[Any]=[term,term]
    clause=" WHERE (title LIKE ? OR body LIKE ?)"
    if entity_type:
        clause += " AND entity_type = ?"
        params.append(entity_type)
    with connect() as con:
        rows=con.execute(
            "SELECT entity_type, entity_id, title FROM search_index"+clause+" ORDER BY entity_type, title LIMIT ?",
            [*params,limit],
        ).fetchall()
    return {"query":q,"count":len(rows),"items":rows_to_dicts(rows)}


@app.get("/api/v1/export/specimens.csv", tags=["Export"])
def export_specimens_csv():
    return _table_export("specimens", "mascarene_paleo_specimens_v0.4.csv")


@app.get("/api/v1/export/darwin-core-occurrence.csv", tags=["Export"])
def export_dwc_csv():
    return _table_export("darwin_core_occurrence", "mascarene_paleo_darwin_core_occurrence_v0.4.csv")


@app.get("/data/{filename}", include_in_schema=False)
def static_data(filename: str):
    safe = Path(filename).name
    path = ROOT / "docs" / "data" / safe
    if not path.exists() or path.suffix != ".json":
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="application/json; charset=utf-8")
