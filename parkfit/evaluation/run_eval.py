"""Evaluation (proposal Section 4.4, objective 6).

Design, after the review of the first draft:
* Each configuration runs the WHOLE pipeline (matching, fusion, inference) on its own
  sources only, so a baseline never sees positions or groupings from a source it excludes.
* A ground-truth facility is joined to a fused feature by verified record identifiers
  (expected_*_id columns, checked by hand against the survey photographs), never by
  proximity. A facility none of the configuration's sources contains is 'unmatched' and is
  scored as not admitted (verdict unknown), which counts as a false negative when the
  vehicle really fits and a true negative when it does not.
* Metrics per profile and pooled: confusion counts, precision, recall, F1, accuracy,
  false-admission rate (FP / (FP + TN)) and balanced accuracy, plus an 'always fits'
  baseline so the class imbalance is visible.
* Every misclassification is assigned to a stage: completeness, fusion, inference,
  granularity.
Outputs: reports/results.json, reports/results.md, reports/figures/*.png
"""
from __future__ import annotations

import json
from collections import Counter

from parkfit.api.scoring import assess
from parkfit.config import REPORTS_DIR
from parkfit.evaluation import ground_truth
from parkfit.evaluation.metrics import Confusion
from parkfit.evaluation.profiles import PROFILES
from parkfit.fusion.engine import fuse_all
from parkfit.matching.matcher import build_groups
from parkfit.schema import FusedFeature, MatchGroup, SourceRecord, VehicleProfile, Verdict

CONFIGS = {
    "osm_only": ({"osm"}, "weighted"),
    "ogd_only": ({"zurich_ogd"}, "weighted"),
    "places_only": ({"places"}, "weighted"),
    "osm+ogd": ({"osm", "zurich_ogd"}, "weighted"),
    "osm+ogd+pls": ({"osm", "zurich_ogd", "pls"}, "weighted"),
    "all_weighted": (None, "weighted"),
    "all_dempster_shafer": (None, "dempster_shafer"),
}


def run_config(by_source: dict[str, list[SourceRecord]], sources: set[str] | None, method: str
               ) -> tuple[list[MatchGroup], list[FusedFeature], dict[str, SourceRecord]]:
    sub = {s: recs for s, recs in by_source.items() if sources is None or s in sources}
    if "pls" in sub and "zurich_ogd" not in sub:
        del sub["pls"]  # operator pages have no coordinates of their own
    groups = build_groups(sub)
    records = {r.key: r for recs in sub.values() for r in recs}
    feats = fuse_all(groups, records, method=method)
    return groups, feats, records


def link_by_id(gt: ground_truth.GroundTruthFeature, groups: list[MatchGroup], feats: list[FusedFeature]
               ) -> FusedFeature | None:
    """The evaluation join: the fused feature whose match group contains a verified record
    key for this facility. Several groups (a matcher split) -> the one with most keys."""
    keys = gt.expected_keys()
    by_id = {f.feature_id: f for f in feats}
    best, best_n = None, 0
    for g in groups:
        n = len(keys & set(g.members))
        if n > best_n and g.group_id in by_id:
            best, best_n = by_id[g.group_id], n
    return best


def source_completeness(gts, by_source) -> dict:
    out = {}
    for src, recs in by_source.items():
        keys = {r.key for r in recs}
        hits = sum(1 for gt in gts if gt.expected_keys() & keys)
        out[src] = {"present": hits, "of": len(gts), "share": round(hits / len(gts), 3)}
    return out


def matching_quality(gts, groups: list[MatchGroup]) -> dict:
    """For facilities with verified ids in two or more sources: did the matcher put all of
    them in one group (tp), leave some apart (fn), or group one with a record of another
    facility (fp)?  Ambiguity-flagged records count as fn (the matcher abstained)."""
    c = Confusion()
    group_of = {m: g for g in groups for m in g.members}
    gt_of_key = {k: gt.gt_id for gt in gts for k in gt.expected_keys()}
    for gt in gts:
        keys = {k for k in gt.expected_keys() if k in group_of}
        if len(keys) < 2:
            continue
        gs = {group_of[k].group_id for k in keys}
        if len(gs) == 1:
            g = group_of[next(iter(keys))]
            foreign = [m for m in g.members if gt_of_key.get(m, gt.gt_id) != gt.gt_id]
            if foreign:
                c.add(True, False, gt=gt.gt_id, reason="grouped with another facility", foreign=foreign)
            else:
                c.add(True, True, gt=gt.gt_id)
        else:
            c.add(False, True, gt=gt.gt_id, reason="split across groups",
                  ambiguous=any(group_of[k].ambiguous for k in keys))
    return c.summary() | {"items": c.items}


def classify(gts, groups, feats, profiles, cfg_name: str) -> dict:
    per_profile, errors, unmatched = {}, [], []
    links = {gt.gt_id: link_by_id(gt, groups, feats) for gt in gts}
    unmatched = [gt.gt_id for gt, f in zip(gts, links.values()) if f is None]
    for p in profiles:
        v = VehicleProfile(**p)
        c = Confusion()
        for gt in gts:
            f = links[gt.gt_id]
            actual = gt.fits(v)
            if f is None:
                c.add(False, actual, gt=gt.gt_id, verdict="unmatched")
                if actual:
                    errors.append({"profile": v.name, "gt": gt.gt_id, "name": gt.name, "stage": "completeness",
                                   "detail": "facility absent from every source in this configuration"})
                continue
            res = assess(f, v, 0.0)
            predicted = res.verdict in (Verdict.FITS, Verdict.TIGHT)
            mh = f.attributes.get("maxheight")
            c.add(predicted, actual, gt=gt.gt_id, verdict=res.verdict.value, score=res.score,
                  fused_height=mh.value if mh else None, kind=mh.kind if mh else None)
            if predicted != actual:
                if "outdoor area" in gt.row.get("height_note", ""):
                    stage = "granularity"
                elif mh and mh.kind == "inferred":
                    stage = "inference"
                else:
                    stage = "fusion"
                errors.append({"profile": v.name, "gt": gt.gt_id, "name": gt.name, "stage": stage,
                               "detail": f"fused height {mh.value if mh else None} ({mh.kind if mh else '-'}, conf "
                                         f"{mh.confidence if mh else '-'}) vs posted {gt.posted_maxheight_m}; bay "
                                         f"{gt.bay_width_m} m; verdict {res.verdict.value}"})
        per_profile[v.name] = c.summary()
    pooled = Confusion()
    for s in per_profile.values():
        pooled.tp += s["tp"]; pooled.fp += s["fp"]; pooled.fn += s["fn"]; pooled.tn += s["tn"]
    # height accuracy, independent of the vehicle
    obs, inf = [], []
    for gt in gts:
        f = links[gt.gt_id]
        if f is None or gt.posted_maxheight_m is None:
            continue
        mh = f.attributes.get("maxheight")
        if mh and mh.value is not None:
            (obs if mh.kind == "observed" else inf).append(abs(float(mh.value) - gt.posted_maxheight_m))
    return {"per_profile": per_profile, "pooled": pooled.summary(), "errors": errors,
            "unmatched": unmatched, "n_features": len(feats),
            "ambiguous": sum(g.ambiguous for g in groups),
            "error_stages": dict(Counter(e["stage"] for e in errors)),
            "height": {"n_observed": len(obs), "mae_observed": round(sum(obs) / len(obs), 3) if obs else None,
                       "within_5cm_observed": round(sum(e <= 0.051 for e in obs) / len(obs), 3) if obs else None,
                       "n_inferred": len(inf), "mae_inferred": round(sum(inf) / len(inf), 3) if inf else None}}


def always_fits(gts, profiles) -> dict:
    per = {}
    pooled = Confusion()
    for p in profiles:
        v = VehicleProfile(**p)
        c = Confusion()
        for gt in gts:
            c.add(True, gt.fits(v), gt=gt.gt_id)
        per[v.name] = c.summary()
        pooled.tp += c.tp; pooled.fp += c.fp; pooled.fn += c.fn; pooled.tn += c.tn
    return {"per_profile": per, "pooled": pooled.summary()}


def label_balance(gts, profiles) -> dict:
    return {p["name"]: {"fits": sum(gt.fits(VehicleProfile(**p)) for gt in gts), "of": len(gts)} for p in profiles}


def run(by_source: dict[str, list[SourceRecord]], groups_unused=None) -> dict:
    gts = ground_truth.load()
    results = {"n_ground_truth": len(gts), "label_balance": label_balance(gts, PROFILES),
               "completeness": source_completeness(gts, by_source), "configs": {},
               "always_fits": always_fits(gts, PROFILES)}
    full_groups = None
    for cfg, (sources, method) in CONFIGS.items():
        if sources and not sources <= set(by_source):
            continue
        groups, feats, records = run_config(by_source, sources, method)
        results["configs"][cfg] = classify(gts, groups, feats, PROFILES, cfg)
        results["configs"][cfg]["matching"] = matching_quality(gts, groups)
        if cfg == "all_weighted":
            full_groups, full_feats, full_records = groups, feats, records
    results["matching"] = results["configs"]["all_weighted"]["matching"]
    results["model_comparison"] = compare_models(full_groups, full_records)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False))
    (REPORTS_DIR / "results.md").write_text(render_markdown(results))
    try:
        from parkfit.evaluation import plots
        plots.make_all(results, gts, full_groups, full_feats)
    except Exception as e:  # noqa: BLE001 - plotting must never break the evaluation
        results["plot_error"] = repr(e)
    return results


def compare_models(groups, records) -> dict:
    w = fuse_all(groups, records, method="weighted", infer=False)
    d = fuse_all(groups, records, method="dempster_shafer", infer=False)
    dmap = {f.feature_id: f for f in d}
    agree = disagree = multi = 0
    details = []
    for fw in w:
        mh = fw.attributes.get("maxheight")
        if not mh or len(mh.supporting) + len(mh.conflicting) < 2:
            continue
        multi += 1
        md = dmap[fw.feature_id].attributes["maxheight"]
        if abs(float(mh.value) - float(md.value)) <= 0.051:
            agree += 1
        else:
            disagree += 1
        details.append({"feature": fw.name, "weighted": mh.value, "weighted_conf": mh.confidence,
                        "ds": md.value, "ds_conf": md.confidence, "ds_conflict_K": md.conflict,
                        "values": [f"{o.value}@{o.provenance.source}" for o in mh.supporting + mh.conflicting]})
    return {"features_with_multiple_height_sources": multi, "agree": agree, "disagree": disagree, "details": details}


def render_markdown(r: dict) -> str:
    intro = (f"Ground-truth facilities: {r['n_ground_truth']}. Each configuration runs matching, fusion and "
             "inference on its own sources only; facilities are joined to fused features by verified record identifiers.")
    L = ["# parkfit evaluation results", "", intro, "", "## Label balance (facilities that really fit, per profile)", "",
         "| profile | fits | of |", "|---|---|---|"]
    for p, v in r["label_balance"].items():
        L.append(f"| {p} | {v['fits']} | {v['of']} |")
    L += ["", "## Source completeness (facility present under a verified identifier)", "", "| source | present | share |", "|---|---|---|"]
    for s, v in r["completeness"].items():
        L.append(f"| {s} | {v['present']}/{v['of']} | {v['share']:.0%} |")
    m = r["matching"]
    L += ["", "## Matching quality, all-sources configuration (facilities with verified ids in >= 2 sources)", "",
          f"precision {m['precision']}, recall {m['recall']}, F1 {m['f1']} (tp {m['tp']}, fp {m['fp']}, fn {m['fn']})", "",
          "## Suitability classification, pooled over the five profiles (115 decisions)", "",
          "| configuration | features | unmatched | TP | FP | FN | TN | precision | recall | F1 | accuracy | false-admission rate | balanced accuracy | height MAE obs (n) | errors by stage |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    af = r["always_fits"]["pooled"]
    L.append(f"| always fits | - | - | {af['tp']} | {af['fp']} | {af['fn']} | {af['tn']} | {af['precision']} | {af['recall']} | {af['f1']} | {af['accuracy']} | {af['false_admission_rate']} | {af['balanced_accuracy']} | - | - |")
    for cfg, v in r["configs"].items():
        mi, h = v["pooled"], v["height"]
        L.append(f"| {cfg} | {v['n_features']} | {len(v['unmatched'])} | {mi['tp']} | {mi['fp']} | {mi['fn']} | {mi['tn']} | {mi['precision']} | {mi['recall']} | {mi['f1']} | {mi['accuracy']} | {mi['false_admission_rate']} | {mi['balanced_accuracy']} | {h['mae_observed']} ({h['n_observed']}) | {v['error_stages']} |")
    L += ["", "## Per-profile F1 / false-admission rate", "",
          "| configuration | " + " | ".join(p["name"] for p in PROFILES) + " |", "|---|" + "---|" * len(PROFILES)]
    L.append("| always fits | " + " | ".join(f"{r['always_fits']['per_profile'][p['name']]['f1']} / {r['always_fits']['per_profile'][p['name']]['false_admission_rate']}" for p in PROFILES) + " |")
    for cfg, v in r["configs"].items():
        L.append(f"| {cfg} | " + " | ".join(f"{v['per_profile'][p['name']]['f1']} / {v['per_profile'][p['name']]['false_admission_rate']}" for p in PROFILES) + " |")
    L += ["", "## Per-profile confusion (TP/FP/FN/TN), all four sources weighted", ""]
    for p in PROFILES:
        s = r["configs"]["all_weighted"]["per_profile"][p["name"]]
        L.append(f"- {p['name']}: {s['tp']}/{s['fp']}/{s['fn']}/{s['tn']}")
    L += ["", "## Unmatched facilities per configuration", ""]
    for cfg, v in r["configs"].items():
        L.append(f"- {cfg}: {', '.join(v['unmatched']) or 'none'}")
    mc = r["model_comparison"]
    L += ["", "## Weighted vs Dempster-Shafer", "",
          f"{mc['features_with_multiple_height_sources']} features have >= 2 height observations; models agree on {mc['agree']}, disagree on {mc['disagree']}.", ""]
    for c in mc["details"]:
        L.append(f"- {c['feature']}: values {c['values']} -> weighted {c['weighted']} (conf {c['weighted_conf']}), DS {c['ds']} (bel {c['ds_conf']}, K={c['ds_conflict_K']})")
    L += ["", "## Error listing (all configurations)", ""]
    for cfg, v in r["configs"].items():
        for e in v["errors"]:
            L.append(f"- [{cfg}] {e['profile']} / {e['gt']} {e['name']}: {e['stage']}: {e['detail']}")
    return "\n".join(L) + "\n"
