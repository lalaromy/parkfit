from datetime import UTC, datetime

from parkfit.ingest import overpass, pls, zurich_ogd


def envelope(payload):
    return {"retrieved_at": datetime.now(UTC).isoformat(), "meta": {}, "payload": payload}


def test_overpass_to_records_filters_and_parses():
    env = envelope({"elements": [
        {"type": "node", "id": 1, "lat": 47.37, "lon": 8.54, "version": 4, "timestamp": "2024-01-01T00:00:00Z",
         "tags": {"amenity": "parking", "parking": "underground", "name": "Parkhaus X", "maxheight": "2,1", "capacity": "100"}},
        {"type": "way", "id": 2, "center": {"lat": 47.37, "lon": 8.54}, "tags": {"amenity": "parking", "parking": "lane"}},
        {"type": "node", "id": 3, "lat": 47.37, "lon": 8.54, "tags": {"amenity": "parking_entrance"}},
    ]})
    recs = overpass.to_records(env)
    assert len(recs) == 1
    attrs = {o.attribute: o.value for o in recs[0].observations}
    assert attrs == {"name": "Parkhaus X", "facility_type": "underground", "maxheight": 2.1, "capacity": 100}
    assert recs[0].observations[2].provenance.version == 4


def test_ogd_to_records():
    env = envelope({"features": [{"geometry": {"coordinates": [8.54, 47.37]},
                                  "properties": {"poi_id": "ph1", "name": "Urania", "kategorie": "Parkhaus",
                                                 "anzahl_oeffentliche_pp": 480.0, "link_pls": "https://x?pid=urania"}},
                                 {"geometry": {"coordinates": [8.0, 47.0]}, "properties": {"poi_id": "far", "name": "Far"}}]})
    recs = zurich_ogd.to_records(env)
    assert len(recs) == 1 and recs[0].extra["link_pls"].endswith("urania")


def test_pls_page_parse():
    txt = "Parkhaus Urania Adresse: Uraniastrasse 3 8001 Zürich Angebot: 607 Plätze ... Einfahrthöhe 2.10m Öffnungszeiten"
    p = pls.parse_page(txt)
    assert p["maxheight"] == 2.1 and p["capacity"] == 607 and p["address"] == "Uraniastrasse 3"
    assert "maxheight" not in pls.parse_page("no height here")
