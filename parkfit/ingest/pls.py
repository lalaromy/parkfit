"""Operator-published facility pages from the Zurich Parkleitsystem (pls-zh.ch, CC0).

The RSS feed lists the garages connected to the guidance system; each garage page is a
small HTML document that usually states 'Einfahrthöhe X.XXm'.  This is the one structured
source that publishes a height, so it is treated as operator evidence (high prior).
"""
from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET

import httpx

from parkfit.config import SOURCE_PRIORS, settings
from parkfit.ingest import cache
from parkfit.ingest.parsers import parse_height_m
from parkfit.schema import Observation, Provenance, SourceRecord

HEIGHT_RE = re.compile(r"(?:Einfahrt|Durchfahrt|Max(?:imal)?)[^\d]{0,15}?h[öo]he\s*[:\-]?\s*(\d[.,]\d{1,2})\s*m", re.IGNORECASE)
PLAETZE_RE = re.compile(r"(\d+)\s*Pl[äa]tze", re.IGNORECASE)
ADDRESS_RE = re.compile(r"Adresse:\s*(.+?)\s+\d{4}\s+Z", re.IGNORECASE)


def fetch_feed(force: bool = False) -> dict:
    if not force:
        cached = cache.load("pls", "feed")
        if cached:
            return cached
    r = httpx.get(settings.pls_feed_url, headers={"User-Agent": settings.user_agent},
                  timeout=60, follow_redirects=True)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    items = []
    for it in root.iter("item"):
        items.append({"title": it.findtext("title"), "link": it.findtext("link"),
                      "description": it.findtext("description")})
    cache.save("pls", "feed", items)
    return cache.load("pls", "feed")


def fetch_page(pid: str, url: str, force: bool = False) -> dict:
    if not force:
        cached = cache.load("pls", f"page_{pid}")
        if cached:
            return cached
    r = httpx.get(url, headers={"User-Agent": settings.user_agent}, timeout=60, follow_redirects=True)
    r.raise_for_status()
    text = re.sub(r"<script.*?</script>", "", r.text, flags=re.DOTALL)
    text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)))
    cache.save("pls", f"page_{pid}", {"text": text, "url": url})
    return cache.load("pls", f"page_{pid}")


def parse_page(text: str) -> dict:
    out: dict = {}
    m = HEIGHT_RE.search(text)
    if m:
        out["maxheight_raw"] = m.group(0)
        out["maxheight"] = parse_height_m(m.group(1))
    m = PLAETZE_RE.search(text)
    if m:
        out["capacity"] = int(m.group(1))
    m = ADDRESS_RE.search(text)
    if m:
        out["address"] = m.group(1).strip()
    return out


def ingest(force: bool = False, coords_from: dict[str, tuple[float, float]] | None = None) -> list[SourceRecord]:
    """PLS pages carry no coordinates.  Positions are taken from the Zurich OGD record that
    links to the same page (`link_pls`), which is an explicit, auditable cross-reference,
    not a fuzzy match."""
    feed = fetch_feed(force)
    out: list[SourceRecord] = []
    for item in feed["payload"]:
        link = item["link"]
        pid = link.split("pid=")[-1]
        if coords_from is None or pid not in coords_from:
            continue
        page = fetch_page(pid, link, force)
        parsed = parse_page(page["payload"]["text"])
        lat, lon = coords_from[pid]
        prov = Provenance(source="pls", source_id=pid, url=link, retrieved_at=cache.retrieved_at(page))
        title = item["title"].split(" / ")[0].strip()
        obs = [Observation(attribute="name", value=title, confidence=SOURCE_PRIORS["pls"]["name"],
                           provenance=prov.model_copy(update={"raw_value": item["title"]}))]
        if parsed.get("maxheight") is not None:
            obs.append(Observation(attribute="maxheight", value=parsed["maxheight"],
                                   confidence=SOURCE_PRIORS["pls"]["maxheight"],
                                   provenance=prov.model_copy(update={"raw_value": parsed["maxheight_raw"]})))
        if parsed.get("capacity"):
            obs.append(Observation(attribute="capacity", value=parsed["capacity"],
                                   confidence=SOURCE_PRIORS["pls"]["capacity"],
                                   provenance=prov.model_copy(update={"raw_value": str(parsed["capacity"])})))
        out.append(SourceRecord(source="pls", source_id=pid, name=title, lat=lat, lon=lon,
                                facility_type="unknown", observations=obs,
                                extra={"address": parsed.get("address"), "status": item.get("description")}))
    return out
