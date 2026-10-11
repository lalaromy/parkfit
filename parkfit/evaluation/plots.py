"""Figures for the report: per-config F1, posted vs fused height, confidence vs error."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parkfit.config import REPORTS_DIR
from parkfit.evaluation.profiles import PROFILES
from parkfit.evaluation.run_eval import link_by_id

FIG = REPORTS_DIR / "figures"


def make_all(results: dict, gts, groups, feats) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    cfgs = [c for c in results["configs"] if c != "all_dempster_shafer"]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    w = 0.8 / len(cfgs)
    for i, cfg in enumerate(cfgs):
        ys = [results["configs"][cfg]["per_profile"][p["name"]]["f1"] for p in PROFILES]
        ax.bar([j + i * w for j in range(len(PROFILES))], ys, w, label=cfg)
    ax.set_xticks([j + 0.4 - w / 2 for j in range(len(PROFILES))])
    ax.set_xticklabels([p["name"].split(" (")[0] for p in PROFILES], rotation=15)
    ax.set_ylabel("F1 (fits / does not fit)"); ax.set_ylim(0, 1.05); ax.legend(fontsize=8)
    ax.set_title("Suitability classification by source configuration")
    fig.tight_layout(); fig.savefig(FIG / "f1_by_profile.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    for gt in gts:
        f = link_by_id(gt, groups, feats)
        if f is None or gt.posted_maxheight_m is None:
            continue
        mh = f.attributes.get("maxheight")
        if not mh or mh.value is None:
            continue
        ax.scatter(gt.posted_maxheight_m, float(mh.value), c="tab:blue" if mh.kind == "observed" else "tab:orange",
                   s=25 + 120 * mh.confidence, alpha=0.7, edgecolor="k")
        ax.annotate(gt.gt_id, (gt.posted_maxheight_m, float(mh.value)), fontsize=6, xytext=(3, 3), textcoords="offset points")
    ax.plot([1.8, 3.5], [1.8, 3.5], "k--", lw=0.8)
    ax.set_xlabel("posted height (ground truth, m)"); ax.set_ylabel("fused height (m)")
    ax.set_title("Fused vs posted height\n(blue = observed, orange = inferred; marker size = confidence)", fontsize=10)
    fig.tight_layout(); fig.savefig(FIG / "height_posted_vs_fused.png", dpi=160); plt.close(fig)
    comp = results["completeness"]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.bar(list(comp), [v["share"] for v in comp.values()], color="tab:gray")
    ax.set_ylim(0, 1.05); ax.set_ylabel("share of ground-truth garages present")
    ax.set_title("Source completeness in the study area")
    fig.tight_layout(); fig.savefig(FIG / "source_completeness.png", dpi=160); plt.close(fig)
