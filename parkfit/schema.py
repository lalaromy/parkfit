"""Canonical data model.

Every source is normalised into `SourceRecord`s carrying `Observation`s.  The fusion
engine never touches raw source formats; it only sees this schema (proposal Section 4.1).
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

Attribute = Literal["maxheight", "capacity", "facility_type", "name", "bay_width", "slope_class"]
FacilityType = Literal["underground", "multi-storey", "surface", "surface_deck", "unknown"]


class Provenance(BaseModel):
    source: str
    source_id: str
    url: str | None = None
    retrieved_at: datetime
    source_timestamp: datetime | None = None  # last edit time where the source exposes it
    version: int | None = None  # OSM object version (intrinsic quality signal)
    raw_value: str | None = None  # the untransformed string, for auditability


class Observation(BaseModel):
    attribute: Attribute
    value: Any
    confidence: float = Field(ge=0.0, le=1.0)
    kind: Literal["observed", "inferred"] = "observed"
    provenance: Provenance | None = None
    note: str | None = None


class SourceRecord(BaseModel):
    """One parking feature as described by one source."""

    source: str
    source_id: str
    name: str | None
    lat: float
    lon: float
    facility_type: FacilityType = "unknown"
    observations: list[Observation] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.source}:{self.source_id}"


class MatchGroup(BaseModel):
    """Records from different sources judged to describe the same real-world facility."""

    group_id: str
    members: list[str]  # record keys
    anchor: str  # the record key used for the canonical position
    name: str | None
    lat: float
    lon: float
    match_scores: dict[str, float] = Field(default_factory=dict)
    ambiguous: bool = False


class FusedAttribute(BaseModel):
    attribute: Attribute
    value: Any
    confidence: float
    kind: Literal["observed", "inferred"]
    supporting: list[Observation] = Field(default_factory=list)
    conflicting: list[Observation] = Field(default_factory=list)
    method: str
    conflict: float = 0.0  # Dempster-Shafer conflict mass K, or weighted dissent share


class FusedFeature(BaseModel):
    feature_id: str
    name: str | None
    lat: float
    lon: float
    sources: list[str]
    attributes: dict[str, FusedAttribute]
    ambiguous_match: bool = False


class VehicleProfile(BaseModel):
    name: str
    height_m: float
    width_m: float
    length_m: float


class Verdict(str, Enum):
    FITS = "fits"
    TIGHT = "tight"
    DOES_NOT_FIT = "does_not_fit"
    UNKNOWN = "unknown"


class DimensionAssessment(BaseModel):
    dimension: str
    verdict: Verdict
    probability_fits: float
    fused: FusedAttribute | None
    explanation: str


class SuitabilityResult(BaseModel):
    feature: FusedFeature
    vehicle: VehicleProfile
    distance_m: float
    score: float  # probability-like suitability in [0,1]
    verdict: Verdict
    assessments: list[DimensionAssessment]
