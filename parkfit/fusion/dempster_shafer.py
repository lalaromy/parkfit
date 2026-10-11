"""Simplified Dempster-Shafer combination for one attribute.

Frame of discernment: the set of distinct (tolerance-bucketed) values reported by any
source.  Each observation is a simple support function: mass `c` on its value and
`1-c` on the whole frame (ignorance).  Dempster's rule combines them; the conflict mass
K is reported so that the report can show where the sources disagree strongly.

Shafer (1976).  Known weakness (Zadeh's paradox): under high conflict the rule can
promote a value nobody supports strongly.  With <= 4 sources and explicit ignorance mass
this is rarely triggered, but K is surfaced precisely so that such cases are auditable.
"""
from __future__ import annotations

from itertools import product

from parkfit.config import settings
from parkfit.schema import FusedAttribute, Observation

THETA = "__theta__"


def _bucket(value, attribute: str, tol: float) -> str:
    if isinstance(value, (int, float)):
        if attribute == "capacity":
            return str(int(round(float(value) / 25.0) * 25))
        return f"{round(float(value) / tol) * tol:.2f}"
    return str(value).strip().lower()


def combine(m1: dict[str, float], m2: dict[str, float]) -> tuple[dict[str, float], float]:
    out: dict[str, float] = {}
    k = 0.0
    for (a, ma), (b, mb) in product(m1.items(), m2.items()):
        if a == THETA:
            key = b
        elif b == THETA or a == b:
            key = a
        else:
            k += ma * mb
            continue
        out[key] = out.get(key, 0.0) + ma * mb
    if k >= 1.0 - 1e-9:
        return {THETA: 1.0}, 1.0
    return {key: v / (1 - k) for key, v in out.items()}, k


def fuse(attribute: str, observations: list[Observation], tolerance: float | None = None) -> FusedAttribute | None:
    obs = [o for o in observations if o.attribute == attribute and o.value is not None]
    if not obs:
        return None
    tol = tolerance if tolerance is not None else settings.numeric_tolerance_m
    m: dict[str, float] = {THETA: 1.0}
    total_k = 0.0
    by_bucket: dict[str, list[Observation]] = {}
    for o in obs:
        b = _bucket(o.value, attribute, tol)
        by_bucket.setdefault(b, []).append(o)
        m, k = combine(m, {b: o.confidence, THETA: 1 - o.confidence})
        total_k = 1 - (1 - total_k) * (1 - k)
    hyps = {k: v for k, v in m.items() if k != THETA}
    best = max(hyps, key=hyps.get)
    winner = by_bucket[best]
    if isinstance(winner[0].value, (int, float)):
        value = round(sum(float(o.value) * o.confidence for o in winner) / sum(o.confidence for o in winner), 2)
    else:
        value = winner[0].value
    conflicting = [o for b, os_ in by_bucket.items() if b != best for o in os_]
    kind = "observed" if any(o.kind == "observed" for o in winner) else "inferred"
    return FusedAttribute(attribute=attribute, value=value, confidence=round(hyps[best], 3), kind=kind,
                          supporting=winner, conflicting=conflicting, method="dempster_shafer",
                          conflict=round(total_k, 3))
