"""Raw-response archive under data/raw/, keyed by source and name, with retrieval timestamps."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from parkfit.config import RAW_DIR


def cache_path(source: str, name: str) -> Path:
    p = RAW_DIR / source / f"{name}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def load(source: str, name: str) -> dict[str, Any] | None:
    p = cache_path(source, name)
    if p.exists():
        return json.loads(p.read_text())
    return None


def save(source: str, name: str, payload: Any, meta: dict[str, Any] | None = None) -> Path:
    p = cache_path(source, name)
    envelope = {
        "retrieved_at": datetime.now(UTC).isoformat(),
        "meta": meta or {},
        "payload": payload,
    }
    p.write_text(json.dumps(envelope, ensure_ascii=False, indent=1))
    return p


def retrieved_at(envelope: dict[str, Any]) -> datetime:
    return datetime.fromisoformat(envelope["retrieved_at"])
