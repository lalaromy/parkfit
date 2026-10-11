from __future__ import annotations

import json
import logging

from parkfit.config import PROCESSED_DIR, STUDY_AREA, settings
from parkfit.fusion.engine import Method, fuse_all
from parkfit.ingest import google_places, overpass, pls, zurich_ogd
from parkfit.matching.matcher import build_groups
from parkfit.schema import FusedFeature, MatchGroup, SourceRecord
from parkfit.storage.db import get_store, save_features_json

log = logging.getLogger("parkfit")


def ingest_all(force: bool = False) -> dict[str, list[SourceRecord]]:
    out: dict[str, list[SourceRecord]] = {}
    if "osm" in settings.sources_enabled:
        out["osm"] = overpass.ingest(STUDY_AREA, force)
        log.info("osm: %d records", len(out["osm"]))
    if "zurich_ogd" in settings.sources_enabled:
        out["zurich_ogd"] = zurich_ogd.ingest(force)
        log.info("zurich_ogd: %d records", len(out["zurich_ogd"]))
    if "pls" in settings.sources_enabled and "zurich_ogd" in out:
        coords = {}
        parent = {}
        for r in out["zurich_ogd"]:
            link = r.extra.get("link_pls")
            if link:
                pid = link.split("pid=")[-1]
                coords[pid] = (r.lat, r.lon)
                parent[pid] = r.key
        recs = pls.ingest(force, coords_from=coords)
        for r in recs:
            r.extra["ogd_key"] = parent[r.source_id]
        out["pls"] = recs
        log.info("pls: %d records", len(recs))
    if "places" in settings.sources_enabled:
        recs = google_places.ingest(STUDY_AREA, force)
        if recs:
            out["places"] = recs
        log.info("places: %d records (%s)", len(recs), "enabled" if settings.google_places_api_key else "no API key, skipped")
    return out


def run(method: Method = "weighted", force: bool = False, store: bool = True
        ) -> tuple[dict[str, list[SourceRecord]], list[MatchGroup], list[FusedFeature]]:
    by_source = ingest_all(force)
    groups = build_groups(by_source)
    records = {r.key: r for recs in by_source.values() for r in recs}
    feats = fuse_all(groups, records, method=method)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "records.json").write_text(json.dumps(
        {k: [r.model_dump(mode="json") for r in v] for k, v in by_source.items()}, ensure_ascii=False))
    (PROCESSED_DIR / "groups.json").write_text(json.dumps([g.model_dump(mode="json") for g in groups], ensure_ascii=False, indent=1))
    save_features_json(feats)
    if store:
        get_store().replace_all(feats)
    return by_source, groups, feats
