from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["dataset_version"] == "0.4"


def test_stats():
    r = client.get("/api/v1/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["specimens"] == 302
    assert data["taxa_unique"] == 30
    assert data["taxa_rows_in_workbook"] == 30
    assert data["publications"] == 32
    assert data["darwin_core_occurrences"] == 302


def test_specimen_detail():
    r = client.get("/api/v1/specimens/MAS-SP-0001")
    assert r.status_code == 200
    data = r.json()
    assert data["specimen_id"] == "MAS-SP-0001"
    assert data["scientific_name"] == "Raphus cucullatus"
    assert data["darwin_core"]["occurrenceID"] == "MAS-SP-0001"


def test_filter_island():
    r = client.get("/api/v1/specimens", params={"island": "Rodrigues", "limit": 5})
    assert r.status_code == 200
    assert r.json()["total"] > 0
    assert all(x["island"] == "Rodrigues" for x in r.json()["items"])


def test_dwc_endpoint():
    r = client.get("/api/v1/dwc/occurrences", params={"basis_of_record": "MaterialCitation"})
    assert r.status_code == 200
    assert r.json()["total"] == 18


def test_clean_primary_keys_and_relationships():
    r = client.get("/api/v1/build-report")
    assert r.status_code == 200
    report = r.json()
    assert report["warnings"] == []
    assert all(not value for value in report["primary_key_checks"].values())
    assert all(not value for value in report["relationship_checks"].values())


def test_taxon_count_is_canonical():
    r = client.get("/api/v1/taxa", params={"limit": 500})
    assert r.status_code == 200
    assert r.json()["total"] == 30

def test_json_explicit_utf8_and_unicode_preserved():
    response = client.get("/api/v1/search", params={"q": "Pezophaps"})
    assert response.status_code == 200
    assert response.headers["content-type"].lower().startswith("application/json; charset=utf-8")
    titles = [item["title"] for item in response.json()["items"]]
    assert any("Gônet" in title for title in titles)
    assert any("Günther" in title for title in titles)
    assert any("André" in title for title in titles)
    assert any(" · Pezophaps solitaria" in title for title in titles)


def test_csv_export_has_utf8_bom():
    response = client.get("/api/v1/export/specimens.csv")
    assert response.status_code == 200
    assert response.content.startswith(b"\xef\xbb\xbf")

