from datetime import UTC, datetime, timedelta

import pytest

from parkfit.fusion import confidence, dempster_shafer, weighted
from parkfit.fusion.dempster_shafer import THETA, combine
from parkfit.schema import Observation
from tests.conftest import obs, prov


def test_weighted_agreement_raises_confidence():
    single = weighted.fuse("maxheight", [obs("maxheight", 2.1, 0.7)])
    both = weighted.fuse("maxheight", [obs("maxheight", 2.1, 0.7), obs("maxheight", 2.10, 0.9, "pls")])
    assert single.value == 2.1 and both.value == 2.1
    assert both.confidence > single.confidence
    assert both.conflict == 0.0


def test_weighted_conflict_picks_heavier_and_records_dissent():
    fa = weighted.fuse("maxheight", [obs("maxheight", 3.6, 0.7), obs("maxheight", 2.0, 0.9, "pls")])
    assert fa.value == 2.0 and len(fa.conflicting) == 1 and fa.conflict > 0


def test_weighted_tolerance_clusters_near_values():
    fa = weighted.fuse("maxheight", [obs("maxheight", 2.05, 0.7), obs("maxheight", 2.1, 0.9, "pls")])
    assert len(fa.supporting) == 2 and 2.05 <= fa.value <= 2.1


def test_ds_combine_and_conflict():
    m, k = combine({"2.10": 0.7, THETA: 0.3}, {"2.10": 0.9, THETA: 0.1})
    assert k == 0 and m["2.10"] > 0.9
    m, k = combine({"2.10": 0.7, THETA: 0.3}, {"3.60": 0.7, THETA: 0.3})
    assert k == pytest.approx(0.49)
    assert m["2.10"] == pytest.approx(m["3.60"])


def test_ds_fuse_reports_k():
    fa = dempster_shafer.fuse("maxheight", [obs("maxheight", 3.6, 0.7), obs("maxheight", 2.0, 0.9, "pls")])
    assert fa.value == 2.0 and fa.conflict > 0.5 and fa.method == "dempster_shafer"


def test_intrinsic_adjustment_only_for_osm():
    old = Observation(attribute="maxheight", value=2.0, confidence=0.7,
                      provenance=prov("osm", version=1, ts=datetime.now(UTC) - timedelta(days=365 * 8)))
    fresh = Observation(attribute="maxheight", value=2.0, confidence=0.7,
                        provenance=prov("osm", version=6, ts=datetime.now(UTC) - timedelta(days=30)))
    assert confidence.adjust(old).confidence < 0.7 < confidence.adjust(fresh).confidence
    pls = obs("maxheight", 2.0, 0.9, "pls")
    assert confidence.adjust(pls).confidence == 0.9
