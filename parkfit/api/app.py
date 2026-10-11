from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from parkfit.api.scoring import assess
from parkfit.evaluation.profiles import PROFILES
from parkfit.schema import SuitabilityResult, VehicleProfile
from parkfit.storage.db import get_store

app = FastAPI(title="parkfit", version="0.1.0",
              description="Multi-source data fusion engine for vehicle-specific parking suitability")
STATIC = Path(__file__).parent / "static"


@app.get("/health")
def health():
    store = get_store()
    return {"status": "ok", "backend": store.backend, "features": store.count()}


@app.get("/profiles")
def profiles():
    return PROFILES


@app.get("/suitability", response_model=list[SuitabilityResult])
def suitability(lat: float = Query(..., ge=-90, le=90), lon: float = Query(..., ge=-180, le=180),
                height: float = Query(..., gt=0, lt=5), width: float = Query(1.9, gt=0, lt=3.5),
                length: float = Query(4.5, gt=0, lt=12), radius: float = Query(600, gt=0, le=5000),
                limit: int = Query(10, ge=1, le=50), include_ambiguous: bool = False):
    store = get_store()
    v = VehicleProfile(name="query", height_m=height, width_m=width, length_m=length)
    results = []
    for feat, dist in store.nearby(lat, lon, radius):
        if feat.ambiguous_match and not include_ambiguous:
            continue
        results.append(assess(feat, v, dist))
    results.sort(key=lambda r: (-r.score, r.distance_m))
    return results[:limit]


@app.get("/features/{feature_id}")
def feature(feature_id: str):
    f = get_store().get(feature_id)
    if f is None:
        raise HTTPException(404, "unknown feature")
    return f


@app.get("/", response_class=HTMLResponse)
def index():
    return (STATIC / "index.html").read_text()
