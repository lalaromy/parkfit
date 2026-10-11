"""Vehicle profile against fused attributes: per-dimension scores, verdicts and explanation text."""
from __future__ import annotations

from parkfit.schema import (
    DimensionAssessment,
    FusedFeature,
    SuitabilityResult,
    VehicleProfile,
    Verdict,
)

# Base rates when the attribute is unknown, set from the surveyed garages (see report).
BASE_RATE_FIT = {"height": 0.80, "width": 0.90}
HEIGHT_TIGHT_M = 0.05   # less than 5 cm clearance -> 'tight' (roof boxes, antennas, loaded vans)
WIDTH_MARGIN_OK = 0.40  # bay width - vehicle width: comfortable door opening
WIDTH_MARGIN_MIN = 0.20 # below this a normal driver cannot open the door


def assess_height(feature: FusedFeature, v: VehicleProfile) -> DimensionAssessment:
    fa = feature.attributes.get("maxheight")
    if fa is None or fa.value is None:
        note = fa.supporting[0].note if fa and fa.supporting else "no height evidence"
        p = fa.confidence if fa else BASE_RATE_FIT["height"]
        return DimensionAssessment(dimension="height", verdict=Verdict.FITS if p > 0.5 else Verdict.UNKNOWN,
                                   probability_fits=round(p, 3), fused=fa,
                                   explanation=f"No structural height limit reported ({note}).")
    limit = float(fa.value)
    clearance = limit - v.height_m
    fits = clearance >= 0
    p = fa.confidence * (1.0 if fits else 0.0) + (1 - fa.confidence) * BASE_RATE_FIT["height"]
    if fits:
        verdict = Verdict.TIGHT if clearance < HEIGHT_TIGHT_M else Verdict.FITS
    else:
        verdict = Verdict.DOES_NOT_FIT
    srcs = ", ".join(sorted({o.provenance.source for o in fa.supporting if o.provenance}))
    expl = (f"Posted/fused max height {limit:.2f} m ({fa.kind}, {fa.method}, from {srcs}, "
            f"confidence {fa.confidence:.2f}); vehicle {v.height_m:.2f} m -> clearance {clearance:+.2f} m.")
    if fa.conflicting:
        expl += " Conflicting values: " + ", ".join(f"{o.value} ({o.provenance.source})" for o in fa.conflicting if o.provenance) + "."
    return DimensionAssessment(dimension="height", verdict=verdict, probability_fits=round(p, 3), fused=fa, explanation=expl)


def assess_width(feature: FusedFeature, v: VehicleProfile) -> DimensionAssessment:
    fa = feature.attributes.get("bay_width")
    if fa is None or fa.value is None:
        return DimensionAssessment(dimension="width", verdict=Verdict.UNKNOWN, probability_fits=BASE_RATE_FIT["width"],
                                   fused=fa, explanation="No bay width evidence.")
    margin = float(fa.value) - v.width_m
    if margin >= WIDTH_MARGIN_OK:
        verdict, fits = Verdict.FITS, True
    elif margin >= WIDTH_MARGIN_MIN:
        verdict, fits = Verdict.TIGHT, True
    else:
        verdict, fits = Verdict.DOES_NOT_FIT, False
    p = fa.confidence * (1.0 if fits else 0.0) + (1 - fa.confidence) * BASE_RATE_FIT["width"]
    expl = (f"Bay width {float(fa.value):.2f} m ({fa.kind}: {fa.supporting[0].note if fa.supporting else ''}); "
            f"vehicle {v.width_m:.2f} m -> margin {margin:+.2f} m.")
    return DimensionAssessment(dimension="width", verdict=verdict, probability_fits=round(p, 3), fused=fa, explanation=expl)


def assess(feature: FusedFeature, v: VehicleProfile, distance_m: float = 0.0) -> SuitabilityResult:
    parts = [assess_height(feature, v), assess_width(feature, v)]
    score = 1.0
    for a in parts:
        score *= a.probability_fits
    verdicts = {a.verdict for a in parts}
    if Verdict.DOES_NOT_FIT in verdicts:
        verdict = Verdict.DOES_NOT_FIT
    elif Verdict.TIGHT in verdicts:
        verdict = Verdict.TIGHT
    elif Verdict.UNKNOWN in verdicts and score < 0.6:
        verdict = Verdict.UNKNOWN
    else:
        verdict = Verdict.FITS
    return SuitabilityResult(feature=feature, vehicle=v, distance_m=round(distance_m, 1),
                             score=round(score, 3), verdict=verdict, assessments=parts)
