from parkfit.evaluation.ground_truth import GroundTruthFeature
from parkfit.evaluation.metrics import Confusion
from parkfit.evaluation.run_eval import link_by_id
from parkfit.fusion.engine import fuse_all
from parkfit.schema import MatchGroup


def gt(gt_id, osm=None, ogd=None, lat=47.37, lon=8.54):
    return GroundTruthFeature(gt_id=gt_id, name="x", facility_type="underground", lat=lat, lon=lon,
                              posted_maxheight_m=2.0, bay_width_m=2.4, slope_deg=10, expected_osm_id=osm,
                              expected_ogd_name=None, expected_ogd_id=ogd, expected_pls_id=None,
                              expected_places_id=None, row={})


def test_join_is_by_identifier_not_proximity(rec_factory):
    recs = {"zurich_ogd:a": rec_factory("zurich_ogd", "a", "Garage A", 47.3700, 8.5400),
            "zurich_ogd:b": rec_factory("zurich_ogd", "b", "Garage B", 47.3702, 8.5400)}
    groups = [MatchGroup(group_id="g0", members=["zurich_ogd:a"], anchor="zurich_ogd:a", name="Garage A", lat=47.37, lon=8.54),
              MatchGroup(group_id="g1", members=["zurich_ogd:b"], anchor="zurich_ogd:b", name="Garage B", lat=47.3702, lon=8.54)]
    feats = fuse_all(groups, recs)
    assert link_by_id(gt("GT1", ogd="b", lat=47.3700), groups, feats).feature_id == "g1"
    assert link_by_id(gt("GT2", ogd="zzz"), groups, feats) is None


def test_false_admission_rate_and_balanced_accuracy():
    c = Confusion()
    for pred, act in [(True, True), (True, True), (True, False), (False, False), (False, False), (False, True)]:
        c.add(pred, act)
    s = c.summary()
    assert s["false_admission_rate"] == round(1 / 3, 3)
    assert s["balanced_accuracy"] == round((2 / 3 + 2 / 3) / 2, 3)
    assert s["positives"] == 3 and s["negatives"] == 3
