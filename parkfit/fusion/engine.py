"""Fusion orchestration: match groups -> fused features with evidence chains."""
from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from parkfit.fusion import confidence, dempster_shafer, inference, weighted
from parkfit.schema import FusedAttribute, FusedFeature, MatchGroup, Observation, SourceRecord

Method = Literal["weighted", "dempster_shafer"]
FUSERS: dict[str, Callable[[str, list[Observation]], FusedAttribute | None]] = {
    "weighted": weighted.fuse,
    "dempster_shafer": dempster_shafer.fuse,
}
ATTRIBUTES = ["name", "facility_type", "maxheight", "capacity"]


def fuse_group(group: MatchGroup, records: dict[str, SourceRecord], method: Method = "weighted",
               sources: set[str] | None = None) -> FusedFeature:
    members = [records[k] for k in group.members if sources is None or records[k].source in sources]
    obs: list[Observation] = [confidence.adjust(o) for r in members for o in r.observations]
    attrs: dict[str, FusedAttribute] = {}
    for a in ATTRIBUTES:
        fa = FUSERS[method](a, obs)
        if fa is not None:
            attrs[a] = fa
    name = str(attrs["name"].value) if "name" in attrs else group.name
    return FusedFeature(feature_id=group.group_id, name=name, lat=group.lat, lon=group.lon,
                        sources=sorted({r.source for r in members}), attributes=attrs,
                        ambiguous_match=group.ambiguous)


def fuse_all(groups: list[MatchGroup], records: dict[str, SourceRecord], method: Method = "weighted",
             sources: set[str] | None = None, infer: bool = True) -> list[FusedFeature]:
    feats = [fuse_group(g, records, method, sources) for g in groups]
    feats = [f for f in feats if f.attributes]  # drop groups whose members were all filtered out
    if infer:
        priors = inference.ContextPriors(feats)
        feats = [inference.fill_missing(f, priors) for f in feats]
    return feats
