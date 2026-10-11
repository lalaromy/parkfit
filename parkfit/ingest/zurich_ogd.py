"""City of Zurich open data: 'Öffentlich zugängliche Parkhäuser' (WFS, CC0).

Provides an authoritative list of publicly accessible garages with address, category and
capacity breakdown, but *no physical dimensions* - which is exactly the gap the fusion
engine has to fill from other sources.
"""
from __future__ import annotations

import httpx

from parkfit.config import SOURCE_PRIORS, STUDY_AREA, BBox, settings
from parkfit.ingest import cache
from parkfit.schema import Observation, Provenance, SourceRecord

CATEGORY_MAP = {"Parkhaus": "underground", "Parkplatz": "surface", "Parkgarage": "underground"}


def fetch(force: bool = False) -> dict:
    name = "parkhaeuser_wfs"
    if not force:
        cached = cache.load("zurich_ogd", name)
        if cached:
            return cached
    params = {
        "SERVICE": "WFS", "REQUEST": "GetFeature", "VERSION": "1.1.0",
        "TYPENAME": "poi_parkhaus_view", "OUTPUTFORMAT": "GeoJSON",
    }
    r = httpx.get(settings.zurich_wfs_url, params=params,
                  headers={"User-Agent": settings.user_agent}, timeout=120, follow_redirects=True)
    r.raise_for_status()
    cache.save("zurich_ogd", name, r.json(), meta={"url": str(r.url)})
    return cache.load("zurich_ogd", name)


def to_records(envelope: dict, bbox: BBox = STUDY_AREA) -> list[SourceRecord]:
    retrieved = cache.retrieved_at(envelope)
    out: list[SourceRecord] = []
    for f in envelope["payload"]["features"]:
        lon, lat = f["geometry"]["coordinates"]
        if not bbox.contains(lat, lon):
            continue
        p = f["properties"]
        sid = str(p.get("poi_id") or p.get("id"))
        prov = Provenance(source="zurich_ogd", source_id=sid,
                          url=p.get("link_pls") or settings.zurich_wfs_url, retrieved_at=retrieved)
        # The dataset is a point-of-interest layer: 'Parkhaus' covers both underground and
        # multi-storey facilities, so the type evidence is deliberately coarse.
        ftype = "underground" if p.get("kategorie") == "Parkhaus" else "surface"
        obs = [
            Observation(attribute="name", value=p["name"], confidence=SOURCE_PRIORS["zurich_ogd"]["name"],
                        provenance=prov.model_copy(update={"raw_value": p["name"]})),
            Observation(attribute="facility_type", value=ftype,
                        confidence=SOURCE_PRIORS["zurich_ogd"]["facility_type"] * 0.7,
                        provenance=prov.model_copy(update={"raw_value": p.get("kategorie")}),
                        note="OGD category 'Parkhaus' does not distinguish underground from multi-storey"),
        ]
        cap = p.get("anzahl_oeffentliche_pp")
        if cap:
            obs.append(Observation(attribute="capacity", value=int(cap),
                                   confidence=SOURCE_PRIORS["zurich_ogd"]["capacity"],
                                   provenance=prov.model_copy(update={"raw_value": str(cap)})))
        out.append(SourceRecord(
            source="zurich_ogd", source_id=sid, name=p["name"], lat=lat, lon=lon,
            facility_type=ftype, observations=obs,
            extra={"adresse": p.get("adresse"), "link_pls": p.get("link_pls"),
                   "small_bays": p.get("davon_klein_pp"), "ev_bays": p.get("davon_elektro_pp"),
                   "municipal": p.get("staedtisch")},
        ))
    return out


def ingest(force: bool = False) -> list[SourceRecord]:
    return to_records(fetch(force))
