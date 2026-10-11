"""Small geodesic helpers; avoids a heavy GIS dependency for point data."""
from __future__ import annotations

import math

EARTH_RADIUS_M = 6_371_008.8


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres between two WGS84 points."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


class GridIndex:
    """A cheap spatial grid index for radius queries on a few thousand points."""

    def __init__(self, cell_deg: float = 0.002):
        self.cell = cell_deg
        self.cells: dict[tuple[int, int], list[int]] = {}
        self.points: list[tuple[float, float]] = []

    def _cell(self, lat: float, lon: float) -> tuple[int, int]:
        return (math.floor(lat / self.cell), math.floor(lon / self.cell))

    def add(self, lat: float, lon: float) -> int:
        idx = len(self.points)
        self.points.append((lat, lon))
        self.cells.setdefault(self._cell(lat, lon), []).append(idx)
        return idx

    def within(self, lat: float, lon: float, radius_m: float) -> list[tuple[int, float]]:
        span = math.ceil(radius_m / (self.cell * 111_000)) + 1
        c0 = self._cell(lat, lon)
        out = []
        for di in range(-span, span + 1):
            for dj in range(-span, span + 1):
                for idx in self.cells.get((c0[0] + di, c0[1] + dj), []):
                    plat, plon = self.points[idx]
                    d = haversine_m(lat, lon, plat, plon)
                    if d <= radius_m:
                        out.append((idx, d))
        return sorted(out, key=lambda t: t[1])
