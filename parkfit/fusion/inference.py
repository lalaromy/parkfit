"""Context priors for attributes no source reports; every value produced here is labelled inferred."""
from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from statistics import median

from parkfit.schema import FusedAttribute, FusedFeature, Observation, Provenance

NORM_PRIORS = {
    "bay_width": {"underground": 2.40, "multi-storey": 2.45, "surface": 2.50, "surface_deck": 2.50, "unknown": 2.40},
    "slope_class": {"underground": "moderate", "multi-storey": "moderate", "surface": "flat",
                    "surface_deck": "flat", "unknown": "moderate"},
    "maxheight": {"underground": 2.00, "multi-storey": 2.00, "surface": None, "surface_deck": None, "unknown": None},
}
INFER_CONF = {"maxheight": 0.35, "bay_width": 0.30, "slope_class": 0.30, "facility_type": 0.40}


class ContextPriors:
    def __init__(self, features: list[FusedFeature]):
        self.by_type: dict[str, list[float]] = defaultdict(list)
        for f in features:
            ft = f.attributes.get("facility_type")
            mh = f.attributes.get("maxheight")
            if ft and mh and mh.kind == "observed":
                self.by_type[str(ft.value)].append(float(mh.value))

    def maxheight(self, facility_type: str) -> tuple[float | None, str]:
        vals = self.by_type.get(facility_type, []) if facility_type != "unknown" else []
        if len(vals) >= 3:
            return round(median(vals), 2), f"median of {len(vals)} observed {facility_type} garages in study area"
        return NORM_PRIORS["maxheight"].get(facility_type), "norm/default prior (too few observed values in study area)"


def _inferred(attribute: str, value, note: str, conf: float) -> FusedAttribute:
    prov = Provenance(source="inference", source_id="context", retrieved_at=datetime.now(UTC))
    obs = Observation(attribute=attribute, value=value, confidence=conf, kind="inferred", provenance=prov, note=note)
    return FusedAttribute(attribute=attribute, value=value, confidence=conf, kind="inferred",
                          supporting=[obs], method="inference")


def fill_missing(feature: FusedFeature, priors: ContextPriors) -> FusedFeature:
    ft_attr = feature.attributes.get("facility_type")
    ft = str(ft_attr.value) if ft_attr else "unknown"
    if ft_attr is None:
        feature.attributes["facility_type"] = _inferred("facility_type", "unknown", "no source reports a type", INFER_CONF["facility_type"])
    if "maxheight" not in feature.attributes:
        val, note = priors.maxheight(ft)
        if ft == "unknown":
            med, mnote = priors.maxheight("underground")
            feature.attributes["maxheight"] = _inferred("maxheight", med, f"facility type unknown; {mnote}", 0.25)
        elif val is None:
            feature.attributes["maxheight"] = _inferred("maxheight", None, f"{ft} parking: no structural height limit expected", 0.60)
        else:
            feature.attributes["maxheight"] = _inferred("maxheight", val, note, INFER_CONF["maxheight"])
    if "bay_width" not in feature.attributes:
        feature.attributes["bay_width"] = _inferred("bay_width", NORM_PRIORS["bay_width"][ft],
                                                    "no source reports bay width; VSS SN 640 291a prior by facility type",
                                                    INFER_CONF["bay_width"])
    if "slope_class" not in feature.attributes:
        feature.attributes["slope_class"] = _inferred("slope_class", NORM_PRIORS["slope_class"][ft],
                                                      "no source reports ramp slope; prior by facility type",
                                                      INFER_CONF["slope_class"])
    return feature
