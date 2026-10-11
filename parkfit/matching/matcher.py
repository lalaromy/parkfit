"""Staged feature matcher: spatial buffer, name similarity, one-to-one assignment, ambiguity flag."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from rapidfuzz import fuzz

from parkfit.config import settings
from parkfit.geo import GridIndex, haversine_m
from parkfit.schema import MatchGroup, SourceRecord

STOPWORDS = {"parkhaus", "parking", "parkgarage", "tiefgarage", "garage", "park", "ag",
             "zürich", "zurich", "zuerich", "city", "einstellhalle", "parkplatz", "ladehaus"}


def normalise_name(name: str | None) -> str:
    if not name:
        return ""
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    s = s.replace("é", "e").replace("ü", "u").replace("ö", "o").replace("ä", "a")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    tokens = [t for t in s.split() if t not in STOPWORDS]
    return " ".join(tokens) or s.strip()


def name_similarity(a: str | None, b: str | None) -> float:
    na, nb = normalise_name(a), normalise_name(b)
    if not na or not nb:
        return 0.0
    return fuzz.token_set_ratio(na, nb) / 100.0


@dataclass
class Candidate:
    key: str
    distance_m: float
    name_sim: float
    type_agree: bool
    score: float


def pair_score(dist_m: float, name_sim: float, type_agree: bool, buffer_m: float,
               exact_name: bool = False) -> float:
    """Combine proximity, name similarity, type agreement and an exact-name bonus into one score in [0, 1]."""
    prox = max(0.0, 1.0 - dist_m / buffer_m)
    s = 0.35 * prox + 0.55 * name_sim + (0.10 if type_agree else 0.0) + (0.05 if exact_name else 0.0)
    return round(min(s, 1.0), 4)


def candidates_for(rec: SourceRecord, others: list[SourceRecord], index: GridIndex,
                   buffer_m: float) -> list[Candidate]:
    out = []
    for idx, d in index.within(rec.lat, rec.lon, buffer_m):
        o = others[idx]
        sim = name_similarity(rec.name, o.name)
        agree = rec.facility_type == o.facility_type or "unknown" in (rec.facility_type, o.facility_type)
        exact = normalise_name(rec.name) == normalise_name(o.name) and bool(normalise_name(rec.name))
        out.append(Candidate(o.key, d, sim, agree, pair_score(d, sim, agree, buffer_m, exact)))
    return sorted(out, key=lambda c: -c.score)


def match_source_pair(a: list[SourceRecord], b: list[SourceRecord],
                      buffer_m: float = settings.match_buffer_m,
                      threshold: float = settings.match_name_threshold,
                      ambiguity_margin: float = 0.10) -> tuple[dict[str, str], set[str]]:
    """Match records in a to b one-to-one; returns (a_key -> b_key, ambiguous a_keys)."""
    index = GridIndex()
    for r in b:
        index.add(r.lat, r.lon)
    proposals: list[tuple[float, str, str]] = []
    ambiguous: set[str] = set()
    for r in a:
        cands = candidates_for(r, b, index, buffer_m)
        if not cands or cands[0].score < threshold:
            continue
        if len(cands) > 1 and cands[1].score >= threshold and cands[0].score - cands[1].score < ambiguity_margin:
            ambiguous.add(r.key)
            continue
        proposals.append((cands[0].score, r.key, cands[0].key))
    mapping: dict[str, str] = {}
    taken: dict[str, str] = {}
    for score, ak, bk in sorted(proposals, reverse=True):
        if bk in taken:
            ambiguous.add(ak)
            continue
        mapping[ak] = bk
        taken[bk] = ak
    return mapping, ambiguous


def build_groups(records_by_source: dict[str, list[SourceRecord]],
                 anchor_source: str = "zurich_ogd",
                 buffer_m: float = settings.match_buffer_m,
                 threshold: float = settings.match_name_threshold) -> list[MatchGroup]:
    """Group records across sources around an anchor source (the register when present)."""
    all_records = {r.key: r for recs in records_by_source.values() for r in recs}
    if anchor_source not in records_by_source:
        anchor_source = next(iter(records_by_source))
    anchors = records_by_source.get(anchor_source, [])
    groups: dict[str, MatchGroup] = {}
    for r in anchors:
        groups[r.key] = MatchGroup(group_id=f"g_{len(groups):04d}", members=[r.key], anchor=r.key,
                                   name=r.name, lat=r.lat, lon=r.lon)
    assigned: set[str] = set(groups)
    ambiguous_all: set[str] = set()
    for src, recs in records_by_source.items():
        if src == anchor_source:
            continue
        if src == "pls":
            for r in recs:
                parent = r.extra.get("ogd_key")
                if parent in groups:
                    groups[parent].members.append(r.key)
                    groups[parent].match_scores[r.key] = 1.0
                    assigned.add(r.key)
            continue
        mapping, amb = match_source_pair(recs, anchors, buffer_m, threshold)
        ambiguous_all |= amb
        for ak, bk in mapping.items():
            g = groups[bk]
            g.members.append(ak)
            rec = all_records[ak]
            g.match_scores[ak] = pair_score(haversine_m(rec.lat, rec.lon, g.lat, g.lon),
                                            name_similarity(rec.name, g.name), True, buffer_m)
            assigned.add(ak)
    for key, rec in all_records.items():
        if key not in assigned:
            g = MatchGroup(group_id=f"g_{len(groups):04d}", members=[key], anchor=key, name=rec.name,
                           lat=rec.lat, lon=rec.lon, ambiguous=key in ambiguous_all)
            groups[key] = g
    return list(groups.values())
