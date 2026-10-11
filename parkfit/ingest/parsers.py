"""Value parsers shared by all sources (OSM tags are free text and need normalising)."""
from __future__ import annotations

import re

_HEIGHT_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(m|meter|metre)?\s*$", re.IGNORECASE)
_FEET_RE = re.compile(r"(\d+)'\s*(\d+)?\"?")


def parse_height_m(raw: str | None) -> float | None:
    """Parse '2.10', '2,1 m', "6'6\"", 'default', 'none' -> metres or None."""
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if s in {"", "default", "none", "no", "unknown", "unlimited"}:
        return None
    m = _FEET_RE.match(s)
    if m:
        ft, inch = int(m.group(1)), int(m.group(2) or 0)
        return round((ft * 12 + inch) * 0.0254, 2)
    m = _HEIGHT_RE.match(s.replace(",", "."))
    if not m:
        return None
    val = float(m.group(1))
    if val > 10:  # someone wrote centimetres
        val = val / 100
    return round(val, 2)


def parse_int(raw) -> int | None:
    if raw is None:
        return None
    try:
        return int(float(str(raw).strip()))
    except ValueError:
        m = re.search(r"\d+", str(raw))
        return int(m.group()) if m else None
