from __future__ import annotations

from parkfit.config import settings
from parkfit.schema import FusedAttribute, Observation


def _clusters(values: list[tuple[float, Observation]], tol: float) -> list[list[Observation]]:
    values = sorted(values, key=lambda t: t[0])
    clusters: list[list[Observation]] = []
    for v, obs in values:
        if clusters and abs(v - float(clusters[-1][-1].value)) <= tol:
            clusters[-1].append(obs)
        else:
            clusters.append([obs])
    return clusters


def noisy_or(confs: list[float]) -> float:
    p = 1.0
    for c in confs:
        p *= 1.0 - c
    return 1.0 - p


def fuse(attribute: str, observations: list[Observation],
         tolerance: float | None = None) -> FusedAttribute | None:
    obs = [o for o in observations if o.attribute == attribute and o.value is not None]
    if not obs:
        return None
    numeric = all(isinstance(o.value, (int, float)) for o in obs)
    if numeric:
        tol = tolerance if tolerance is not None else (settings.numeric_tolerance_m if attribute == "maxheight" else 0)
        if attribute == "capacity":
            tol = max(5, 0.15 * max(float(o.value) for o in obs))
        clusters = _clusters([(float(o.value), o) for o in obs], tol)
    else:
        buckets: dict[str, list[Observation]] = {}
        for o in obs:
            buckets.setdefault(str(o.value).strip().lower(), []).append(o)
        clusters = list(buckets.values())
    weights = [sum(o.confidence for o in c) for c in clusters]
    total = sum(weights)
    best = max(range(len(clusters)), key=lambda i: weights[i])
    winner = clusters[best]
    if numeric:
        value = sum(float(o.value) * o.confidence for o in winner) / weights[best]
        value = round(value, 2)
    else:
        value = max(winner, key=lambda o: o.confidence).value
    share = weights[best] / total
    conf = round(noisy_or([o.confidence for o in winner]) * share, 3)
    conflicting = [o for i, c in enumerate(clusters) if i != best for o in c]
    kind = "observed" if any(o.kind == "observed" for o in winner) else "inferred"
    return FusedAttribute(attribute=attribute, value=value, confidence=conf, kind=kind,
                          supporting=winner, conflicting=conflicting, method="weighted",
                          conflict=round(1 - share, 3))
