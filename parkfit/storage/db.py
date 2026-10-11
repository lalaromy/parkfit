"""Fused-feature store with two interchangeable backends.

* SqliteStore  - zero setup; radius search by haversine over a bbox pre-filter.
* PostgisStore - used when DATABASE_URL points at PostGIS (docker compose up -d);
                 radius search via ST_DWithin on a geography column with a GiST index.

Both store the fused feature as JSON next to its geometry so that the evidence chain is
served verbatim.  The abstraction exists because the proposal committed to PostGIS while
the evaluation must be runnable by a marker with nothing but Python installed.
"""
from __future__ import annotations

import json
from functools import lru_cache

from sqlalchemy import Column, Float, MetaData, String, Table, Text, create_engine, select, text

from parkfit.config import PROCESSED_DIR, settings
from parkfit.geo import haversine_m
from parkfit.schema import FusedFeature

metadata = MetaData()
features = Table(
    "fused_features", metadata,
    Column("feature_id", String, primary_key=True),
    Column("name", String),
    Column("lat", Float, nullable=False),
    Column("lon", Float, nullable=False),
    Column("payload", Text, nullable=False),
)


class SqliteStore:
    backend = "sqlite"

    def __init__(self, url: str | None = None):
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(url or f"sqlite:///{PROCESSED_DIR / 'parkfit.sqlite'}")
        metadata.create_all(self.engine)

    def replace_all(self, feats: list[FusedFeature]) -> None:
        with self.engine.begin() as con:
            con.execute(features.delete())
            con.execute(features.insert(), [
                {"feature_id": f.feature_id, "name": f.name, "lat": f.lat, "lon": f.lon,
                 "payload": f.model_dump_json()} for f in feats])

    def count(self) -> int:
        with self.engine.connect() as con:
            return con.execute(text("select count(*) from fused_features")).scalar_one()

    def get(self, feature_id: str) -> FusedFeature | None:
        with self.engine.connect() as con:
            row = con.execute(select(features.c.payload).where(features.c.feature_id == feature_id)).first()
        return FusedFeature.model_validate_json(row[0]) if row else None

    def nearby(self, lat: float, lon: float, radius_m: float) -> list[tuple[FusedFeature, float]]:
        dlat = radius_m / 111_000
        dlon = radius_m / (111_000 * 0.68)
        with self.engine.connect() as con:
            rows = con.execute(select(features.c.payload, features.c.lat, features.c.lon).where(
                features.c.lat.between(lat - dlat, lat + dlat), features.c.lon.between(lon - dlon, lon + dlon))).all()
        out = []
        for payload, flat, flon in rows:
            d = haversine_m(lat, lon, flat, flon)
            if d <= radius_m:
                out.append((FusedFeature.model_validate_json(payload), d))
        return sorted(out, key=lambda t: t[1])


class PostgisStore(SqliteStore):
    backend = "postgis"

    def __init__(self, url: str):
        self.engine = create_engine(url)
        with self.engine.begin() as con:
            con.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            con.execute(text("""
                CREATE TABLE IF NOT EXISTS fused_features (
                  feature_id text PRIMARY KEY, name text, lat double precision, lon double precision,
                  payload jsonb NOT NULL, geom geography(Point, 4326))"""))
            con.execute(text("CREATE INDEX IF NOT EXISTS fused_features_geom_idx ON fused_features USING GIST (geom)"))

    def replace_all(self, feats: list[FusedFeature]) -> None:
        with self.engine.begin() as con:
            con.execute(text("DELETE FROM fused_features"))
            for f in feats:
                con.execute(text("""INSERT INTO fused_features (feature_id, name, lat, lon, payload, geom)
                                    VALUES (:id, :name, :lat, :lon, CAST(:payload AS jsonb),
                                            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography)"""),
                            {"id": f.feature_id, "name": f.name, "lat": f.lat, "lon": f.lon,
                             "payload": f.model_dump_json()})

    def nearby(self, lat: float, lon: float, radius_m: float) -> list[tuple[FusedFeature, float]]:
        with self.engine.connect() as con:
            rows = con.execute(text("""
                SELECT payload::text, ST_Distance(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography) AS d
                FROM fused_features
                WHERE ST_DWithin(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, :r)
                ORDER BY d"""), {"lat": lat, "lon": lon, "r": radius_m}).all()
        return [(FusedFeature.model_validate_json(p), float(d)) for p, d in rows]


@lru_cache(maxsize=1)
def get_store():
    if settings.database_url and settings.database_url.startswith("postgresql"):
        return PostgisStore(settings.database_url)
    return SqliteStore()


def save_features_json(feats: list[FusedFeature], name: str = "fused_features.json") -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / name).write_text(json.dumps([f.model_dump(mode="json") for f in feats], ensure_ascii=False, indent=1))
