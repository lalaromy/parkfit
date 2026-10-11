import pytest
from fastapi.testclient import TestClient

from parkfit.api import app as app_module
from parkfit.fusion.engine import fuse_all
from parkfit.schema import MatchGroup
from parkfit.storage.db import SqliteStore


@pytest.fixture
def client(rec_factory, tmp_path, monkeypatch):
    store = SqliteStore(f"sqlite:///{tmp_path/'t.sqlite'}")
    recs = {"zurich_ogd:p1": rec_factory("zurich_ogd", "p1", "Urania", 47.37437, 8.54075, capacity=480),
            "osm:n1": rec_factory("osm", "n1", "Parkhaus Urania", 47.3744, 8.5408, maxheight=2.1)}
    g = MatchGroup(group_id="g0", members=list(recs), anchor="zurich_ogd:p1", name="Urania", lat=47.37437, lon=8.54075)
    store.replace_all(fuse_all([g], recs))
    monkeypatch.setattr(app_module, "get_store", lambda: store)
    return TestClient(app_module.app)


def test_health_and_query(client):
    assert client.get("/health").json()["features"] == 1
    r = client.get("/suitability", params={"lat": 47.3745, "lon": 8.5405, "height": 1.99, "width": 1.9})
    assert r.status_code == 200
    body = r.json()
    assert body[0]["feature"]["name"] == "Urania"
    assert body[0]["verdict"] in ("fits", "tight")
    assert "clearance" in body[0]["assessments"][0]["explanation"]
    r = client.get("/suitability", params={"lat": 47.3745, "lon": 8.5405, "height": 2.6})
    assert r.json()[0]["verdict"] == "does_not_fit"


def test_validation(client):
    assert client.get("/suitability", params={"lat": 95, "lon": 8, "height": 2}).status_code == 422
    assert client.get("/features/nope").status_code == 404
