from __future__ import annotations

from datetime import UTC, datetime

from parkfit.schema import Observation


def adjust(obs: Observation, now: datetime | None = None) -> Observation:
    if obs.provenance is None or obs.provenance.source != "osm":
        return obs
    now = now or datetime.now(UTC)
    c = obs.confidence
    v = obs.provenance.version or 1
    if v >= 5:
        c += 0.05
    elif v == 1:
        c -= 0.05
    ts = obs.provenance.source_timestamp
    if ts is not None:
        age_years = (now - ts).days / 365.25
        if age_years < 2:
            c += 0.05
        elif age_years > 6:
            c -= 0.05
    return obs.model_copy(update={"confidence": max(0.05, min(0.95, round(c, 3)))})
