from __future__ import annotations

import json
import logging

import typer

app = typer.Typer(help="parkfit: multi-source parking suitability fusion engine")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@app.command()
def ingest(force: bool = typer.Option(False, help="ignore the raw cache and re-fetch")):
    """Fetch all enabled sources into data/raw and print record counts."""
    from parkfit.pipeline import ingest_all
    for src, recs in ingest_all(force).items():
        typer.echo(f"{src}: {len(recs)} records")


@app.command()
def run(method: str = typer.Option("weighted", help="weighted | dempster_shafer"),
        force: bool = False):
    """Ingest -> match -> fuse -> store (SQLite or PostGIS)."""
    from parkfit.pipeline import run as _run
    _by_source, groups, feats = _run(method=method, force=force)  # type: ignore[arg-type]
    typer.echo(f"groups: {len(groups)}  fused features: {len(feats)}  "
               f"ambiguous: {sum(g.ambiguous for g in groups)}")


@app.command()
def evaluate():
    """Run the full evaluation against the ground truth and write reports/."""
    from parkfit.evaluation.run_eval import run as _eval
    from parkfit.pipeline import ingest_all
    by_source = ingest_all()
    res = _eval(by_source)
    typer.echo(json.dumps({k: {m: v["pooled"][m] for m in ("f1", "false_admission_rate", "balanced_accuracy")}
                           for k, v in res["configs"].items()}, indent=1))
    typer.echo("written: reports/results.md, reports/results.json, reports/figures/")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Start the query API and demo page."""
    import uvicorn
    uvicorn.run("parkfit.api.app:app", host=host, port=port, reload=reload)


@app.command()
def query(lat: float, lon: float, height: float, width: float = 1.9, radius: float = 600):
    """Ask the engine directly (no server needed)."""
    from parkfit.api.scoring import assess
    from parkfit.schema import VehicleProfile
    from parkfit.storage.db import get_store
    v = VehicleProfile(name="cli", height_m=height, width_m=width, length_m=4.5)
    for f, d in get_store().nearby(lat, lon, radius):
        r = assess(f, v, d)
        typer.echo(f"{r.verdict.value:13s} {r.score:.2f}  {d:5.0f} m  {f.name}")
        for a in r.assessments:
            typer.echo(f"    - {a.explanation}")
