from parkfit.api.scoring import assess
from parkfit.fusion.engine import fuse_all
from parkfit.schema import FusedAttribute, FusedFeature, MatchGroup, VehicleProfile, Verdict
from tests.conftest import obs


def feature(height, conf, kind="observed", width=2.4):
    attrs = {
        "maxheight": FusedAttribute(attribute="maxheight", value=height, confidence=conf, kind=kind,
                                    supporting=[obs("maxheight", height, conf)], method="weighted"),
        "bay_width": FusedAttribute(attribute="bay_width", value=width, confidence=0.3, kind="inferred",
                                    supporting=[obs("bay_width", width, 0.3, "inference", "inferred")], method="inference"),
    }
    return FusedFeature(feature_id="f", name="x", lat=0, lon=0, sources=["osm"], attributes=attrs)


def test_van_does_not_fit_under_2m():
    r = assess(feature(2.0, 0.9), VehicleProfile(name="van", height_m=1.99, width_m=1.9, length_m=5))
    assert r.verdict == Verdict.TIGHT
    r = assess(feature(1.9, 0.9), VehicleProfile(name="van", height_m=1.99, width_m=1.9, length_m=5))
    assert r.verdict == Verdict.DOES_NOT_FIT and r.score < 0.2


def test_low_confidence_degrades_to_prior():
    sure = assess(feature(1.9, 0.95), VehicleProfile(name="van", height_m=1.99, width_m=1.9, length_m=5))
    unsure = assess(feature(1.9, 0.35, "inferred"), VehicleProfile(name="van", height_m=1.99, width_m=1.9, length_m=5))
    assert unsure.score > sure.score


def test_no_limit_feature():
    f = feature(2.0, 0.9)
    f.attributes["maxheight"] = FusedAttribute(attribute="maxheight", value=None, confidence=0.6, kind="inferred",
                                               supporting=[obs("maxheight", None, 0.6, "inference", "inferred")], method="inference")
    r = assess(f, VehicleProfile(name="hi", height_m=2.6, width_m=2.0, length_m=6))
    assert r.assessments[0].verdict == Verdict.FITS


def test_inference_fills_missing(rec_factory):
    recs = {"zurich_ogd:p1": rec_factory("zurich_ogd", "p1", "Nowhere", 47.37, 8.54, capacity=50)}
    g = MatchGroup(group_id="g0", members=["zurich_ogd:p1"], anchor="zurich_ogd:p1", name="Nowhere", lat=47.37, lon=8.54)
    feats = fuse_all([g], recs, method="weighted")
    mh = feats[0].attributes["maxheight"]
    assert mh.kind == "inferred" and mh.confidence < 0.5
    assert feats[0].attributes["bay_width"].kind == "inferred"
