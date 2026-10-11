"""Central configuration: study area, paths, API settings and per-source confidence priors."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
GROUND_TRUTH_CSV = DATA_DIR / "ground_truth" / "zurich_garages_2026.csv"
REPORTS_DIR = ROOT / "reports"


@dataclass(frozen=True)
class BBox:
    """Study area as a WGS84 bounding box (south, west, north, east)."""

    south: float
    west: float
    north: float
    east: float

    def contains(self, lat: float, lon: float) -> bool:
        return self.south <= lat <= self.north and self.west <= lon <= self.east

    def overpass(self) -> str:
        return f"{self.south},{self.west},{self.north},{self.east}"


STUDY_AREA = BBox(south=47.355, west=8.515, north=47.395, east=8.565)


@dataclass
class Settings:
    user_agent: str = os.getenv("PARKFIT_USER_AGENT", "parkfit-msc-project/0.1")
    google_places_api_key: str | None = os.getenv("GOOGLE_PLACES_API_KEY") or None
    database_url: str | None = os.getenv("DATABASE_URL") or None
    overpass_url: str = "https://overpass-api.de/api/interpreter"
    zurich_wfs_url: str = (
        "https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Oeffentlich_zugaengliche_Parkhaeuser"
    )
    pls_feed_url: str = "https://www.pls-zh.ch/plsFeed/rss"
    match_buffer_m: float = 120.0
    match_name_threshold: float = 0.55
    numeric_tolerance_m: float = 0.051  # values within 5 cm are treated as agreeing
    sources_enabled: list[str] = field(default_factory=lambda: ["osm", "zurich_ogd", "pls", "places"])


settings = Settings()

SOURCE_PRIORS: dict[str, dict[str, float]] = {
    "osm": {"maxheight": 0.70, "capacity": 0.65, "facility_type": 0.80, "name": 0.80},
    "zurich_ogd": {"capacity": 0.90, "facility_type": 0.95, "name": 0.95},
    "pls": {"maxheight": 0.90, "capacity": 0.85, "name": 0.90},
    "places": {"facility_type": 0.70, "name": 0.85},
}
