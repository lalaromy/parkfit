from __future__ import annotations

import csv
from dataclasses import dataclass

from parkfit.api.scoring import WIDTH_MARGIN_MIN
from parkfit.config import GROUND_TRUTH_CSV
from parkfit.schema import VehicleProfile


@dataclass
class GroundTruthFeature:
    gt_id: str
    name: str
    facility_type: str
    lat: float
    lon: float
    posted_maxheight_m: float | None
    bay_width_m: float
    slope_deg: float
    expected_osm_id: str | None
    expected_ogd_name: str | None
    expected_ogd_id: str | None
    expected_pls_id: str | None
    expected_places_id: str | None
    row: dict

    def expected_keys(self) -> set[str]:
        """Record keys (source:id) that describe this facility, verified by hand against the
        survey photographs and each source's record (see docs/ground_truth_protocol.md)."""
        keys = set()
        if self.expected_osm_id:
            keys.add(f"osm:{self.expected_osm_id}")
        if self.expected_ogd_id:
            keys.add(f"zurich_ogd:{self.expected_ogd_id}")
        if self.expected_pls_id:
            keys.add(f"pls:{self.expected_pls_id}")
        if self.expected_places_id:
            keys.add(f"places:{self.expected_places_id}")
        return keys

    def fits(self, v: VehicleProfile) -> bool:
        """Binary label: fits if under the posted height limit and the measured bay leaves
        at least WIDTH_MARGIN_MIN of door clearance."""
        h_ok = self.posted_maxheight_m is None or v.height_m <= self.posted_maxheight_m
        w_ok = (self.bay_width_m - v.width_m) >= WIDTH_MARGIN_MIN
        return h_ok and w_ok


def load(path=GROUND_TRUTH_CSV) -> list[GroundTruthFeature]:
    out = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out.append(GroundTruthFeature(
                gt_id=row["gt_id"], name=row["name"], facility_type=row["facility_type"],
                lat=float(row["lat"]), lon=float(row["lon"]),
                posted_maxheight_m=float(row["posted_maxheight_m"]) if row["posted_maxheight_m"] else None,
                bay_width_m=float(row["bay_width_cm"]) / 100.0,
                slope_deg=float(row["clino_top_deg"]),
                expected_osm_id=row["expected_osm_id"] or None,
                expected_ogd_name=row["expected_ogd_name"] or None,
                expected_ogd_id=row.get("expected_ogd_id") or None,
                expected_pls_id=row.get("expected_pls_id") or None,
                expected_places_id=row.get("expected_places_id") or None, row=row))
    return out
