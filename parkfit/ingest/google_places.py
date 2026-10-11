"""Google Places (New) adapter; filters non-car places; snapshot usable offline without a key."""
from __future__ import annotations

import re

import httpx

from parkfit.config import SOURCE_PRIORS, STUDY_AREA, BBox, settings
from parkfit.ingest import cache
from parkfit.schema import Observation, Provenance, SourceRecord

ENDPOINT = "https://places.googleapis.com/v1/places:searchNearby"
FIELD_MASK = "places.id,places.displayName,places.location,places.primaryType,places.types"


def fetch(bbox: BBox = STUDY_AREA, force: bool = False) -> dict | None:
    name = f"nearby_{bbox.overpass().replace(',', '_')}"
    if not force:
        cached = cache.load("places", name)
        if cached:
            return cached
    if not settings.google_places_api_key:
        return None
    lat_step, lon_step = 0.0075, 0.011
    places: dict[str, dict] = {}
    lat = bbox.south
    while lat <= bbox.north:
        lon = bbox.west
        while lon <= bbox.east:
            body = {
                "includedTypes": ["parking"], "maxResultCount": 20,
                "locationRestriction": {"circle": {"center": {"latitude": lat, "longitude": lon},
                                                   "radius": 600.0}},
            }
            r = httpx.post(ENDPOINT, json=body, timeout=60,
                           headers={"X-Goog-Api-Key": settings.google_places_api_key,
                                    "X-Goog-FieldMask": FIELD_MASK})
            r.raise_for_status()
            for p in r.json().get("places", []):
                places[p["id"]] = p
            lon += lon_step
        lat += lat_step
    cache.save("places", name, list(places.values()), meta={"bbox": bbox.overpass()})
    return cache.load("places", name)


KEEP_PRIMARY = {"parking_garage", "parking_lot", "parking"}
EXCLUDE_NAME = re.compile(r"velo|fahrrad|bike|bicycle|motorrad|motocycle|motorcycle|behinderten|disabled|"
                          r"nicht .ffentlich|dauermieter|car wash|wash", re.IGNORECASE)
PRIMARY_TYPE_MAP = {"parking_garage": "underground"}


def to_records(envelope: dict, bbox: BBox = STUDY_AREA) -> list[SourceRecord]:
    retrieved = cache.retrieved_at(envelope)
    out = []
    for p in envelope["payload"]:
        lat, lon = p["location"]["latitude"], p["location"]["longitude"]
        if not bbox.contains(lat, lon):
            continue
        name = (p.get("displayName") or {}).get("text")
        primary = p.get("primaryType")
        if primary not in KEEP_PRIMARY or (name and EXCLUDE_NAME.search(name)):
            continue
        prov = Provenance(source="places", source_id=p["id"], retrieved_at=retrieved,
                          url=f"https://www.google.com/maps/place/?q=place_id:{p['id']}")
        obs = []
        if name:
            obs.append(Observation(attribute="name", value=name, confidence=SOURCE_PRIORS["places"]["name"],
                                   provenance=prov))
        ftype = PRIMARY_TYPE_MAP.get(primary, "unknown")
        if ftype != "unknown":
            obs.append(Observation(attribute="facility_type", value=ftype,
                                   confidence=SOURCE_PRIORS["places"]["facility_type"] * 0.7,
                                   provenance=prov.model_copy(update={"raw_value": primary}),
                                   note="Places 'parking_garage' does not distinguish underground from multi-storey"))
        out.append(SourceRecord(source="places", source_id=p["id"], name=name, lat=lat, lon=lon,
                                facility_type=ftype, observations=obs,
                                extra={"types": p.get("types", []), "primary_type": primary}))
    return out


def ingest(bbox: BBox = STUDY_AREA, force: bool = False) -> list[SourceRecord]:
    env = fetch(bbox, force)
    return to_records(env, bbox) if env else []
