"""OpenStreetMap adapter via Overpass (out meta, so version and timestamp reach provenance)."""
from __future__ import annotations

from datetime import UTC, datetime

import httpx

from parkfit.config import SOURCE_PRIORS, STUDY_AREA, BBox, settings
from parkfit.ingest import cache
from parkfit.ingest.parsers import parse_height_m, parse_int
from parkfit.schema import Observation, Provenance, SourceRecord

QUERY = """
[out:json][timeout:120];
(
  nwr["amenity"="parking"]({bbox});
  nwr["amenity"="parking_entrance"]({bbox});
);
out meta center;
"""

OSM_TYPE_MAP = {
    "underground": "underground",
    "multi-storey": "multi-storey",
    "rooftop": "multi-storey",
    "surface": "surface",
    "street_side": "surface",
    "lane": "surface",
    "carports": "surface_deck",
    "garage_boxes": "surface_deck",
}


def fetch(bbox: BBox = STUDY_AREA, force: bool = False) -> dict:
    name = f"parking_{bbox.overpass().replace(',', '_')}"
    if not force:
        cached = cache.load("osm", name)
        if cached:
            return cached
    r = httpx.post(
        settings.overpass_url,
        data={"data": QUERY.format(bbox=bbox.overpass())},
        headers={"User-Agent": settings.user_agent, "Accept": "application/json"},
        timeout=180,
    )
    r.raise_for_status()
    cache.save("osm", name, r.json(), meta={"bbox": bbox.overpass(), "query": QUERY})
    return cache.load("osm", name)


def to_records(envelope: dict, include_unnamed_surface: bool = False) -> list[SourceRecord]:
    """Convert Overpass elements to canonical records; unnamed lane/street-side parking is dropped."""
    retrieved = cache.retrieved_at(envelope)
    out: list[SourceRecord] = []
    for el in envelope["payload"].get("elements", []):
        tags = el.get("tags", {})
        if tags.get("amenity") != "parking":
            continue
        ftype = OSM_TYPE_MAP.get(tags.get("parking", ""), "unknown")
        name = tags.get("name")  # operator is kept in extra, not used as a name: it labels lots, not facilities
        if not include_unnamed_surface and name is None and ftype in {"surface", "unknown"}:
            continue
        if "center" in el:
            lat, lon = el["center"]["lat"], el["center"]["lon"]
        else:
            lat, lon = el["lat"], el["lon"]
        sid = f"{el['type']}/{el['id']}"
        ts = el.get("timestamp")
        prov = Provenance(
            source="osm",
            source_id=sid,
            url=f"https://www.openstreetmap.org/{sid}",
            retrieved_at=retrieved,
            source_timestamp=datetime.fromisoformat(ts) if ts else None,
            version=el.get("version"),
        )
        obs: list[Observation] = []
        if name:
            obs.append(
                Observation(attribute="name", value=name, confidence=SOURCE_PRIORS["osm"]["name"],
                            provenance=prov.model_copy(update={"raw_value": name}))
            )
        if ftype != "unknown":
            obs.append(
                Observation(attribute="facility_type", value=ftype,
                            confidence=SOURCE_PRIORS["osm"]["facility_type"],
                            provenance=prov.model_copy(update={"raw_value": tags.get("parking")}))
            )
        if "maxheight" in tags:
            h = parse_height_m(tags["maxheight"])
            if h is not None:
                obs.append(
                    Observation(attribute="maxheight", value=h,
                                confidence=SOURCE_PRIORS["osm"]["maxheight"],
                                provenance=prov.model_copy(update={"raw_value": tags["maxheight"]}))
                )
        if "capacity" in tags:
            c = parse_int(tags["capacity"])
            if c is not None:
                obs.append(
                    Observation(attribute="capacity", value=c,
                                confidence=SOURCE_PRIORS["osm"]["capacity"],
                                provenance=prov.model_copy(update={"raw_value": tags["capacity"]}))
                )
        out.append(
            SourceRecord(source="osm", source_id=sid, name=name, lat=lat, lon=lon,
                         facility_type=ftype, observations=obs,
                         extra={"tags": tags, "version": el.get("version"), "timestamp": ts})
        )
    return out


def ingest(bbox: BBox = STUDY_AREA, force: bool = False) -> list[SourceRecord]:
    return to_records(fetch(bbox, force))


def _now() -> datetime:
    return datetime.now(UTC)
