"""Deterministic OzBargain feed fetch + parse. No LLM, no GCP — pure and testable.

The scout *tool* (agents/scouts.py) wraps this; the LLM normalises the raw dicts
into the Offer schema and filters to the user's programs. Keeping the scrape here
means we can unit-test parsing against fixtures and prove correctness offline.

Etiquette: OzBargain robots.txt allows /deals/feed and /tag/*/feed (disallows /api,
/goto, /search, etc. — none used here). We send an identifying UA, fetch one feed
per run, and never follow the /goto/ redirect (we use the real merchant url from
the <ozb:meta> block instead).
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import httpx

OZB_BASE = "https://www.ozbargain.com.au"
OZB_NS = "https://www.ozbargain.com.au"  # xmlns:ozb in the feed
USER_AGENT = "DuckFleetBot/0.1 (+https://duckfleet.dev; loyalty-points research; contact duckfleet.dev@gmail.com)"

# Merchant -> loyalty program the purchase EARNS in (a hint, not authoritative;
# the valuer LLM confirms). Addresses the "a Coles deal has no intrinsic program,
# it earns points via the merchant" problem.
MERCHANT_PROGRAM = {
    "coles": "flybuys",
    "woolworths": "everyday_rewards",
    "bigw": "everyday_rewards",
    "big w": "everyday_rewards",
}
# Keyword -> program, scanned over title + categories.
KEYWORD_PROGRAM = {
    "qantas": "qantas_ff",
    "frequent flyer": "qantas_ff",
    "velocity": "velocity",
    "flybuys": "flybuys",
    "everyday rewards": "everyday_rewards",
}

_PRICE_RE = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
_MERCHANT_RE = re.compile(r"@\s*([^@]+?)\s*$")


def _ozb(tag: str) -> str:
    return f"{{{OZB_NS}}}{tag}"


def _parse_price_aud(title: str) -> float | None:
    m = _PRICE_RE.search(title or "")
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def _parse_merchant(title: str) -> str | None:
    m = _MERCHANT_RE.search(title or "")
    return m.group(1).strip() if m else None


def _program_hint(title: str, merchant: str | None, categories: list[str]) -> str | None:
    hay = " ".join([title or "", *(categories or [])]).lower()
    for kw, prog in KEYWORD_PROGRAM.items():
        if kw in hay:
            return prog
    if merchant:
        ml = merchant.lower()
        for name, prog in MERCHANT_PROGRAM.items():
            if name in ml:
                return prog
    return None


def _int_or_none(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def parse_feed(xml_bytes: bytes) -> list[dict]:
    """Parse an OzBargain RSS feed into raw deal dicts. Pure function — unit-testable."""
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    if channel is None:
        return []
    deals: list[dict] = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        node_url = (item.findtext("link") or "").strip()
        categories = [c.text.strip() for c in item.findall("category") if c.text]

        meta = item.find(_ozb("meta"))
        merchant_url = meta.get("url") if meta is not None else None
        expiry = meta.get("expiry") if meta is not None else None
        click_count = _int_or_none(meta.get("click-count")) if meta is not None else None
        votes_pos = _int_or_none(meta.get("votes-pos")) if meta is not None else None
        votes_neg = _int_or_none(meta.get("votes-neg")) if meta is not None else None

        title_msg = item.find(_ozb("title-msg"))
        status = title_msg.get("type") if title_msg is not None else None  # expired/upcoming/...

        merchant = _parse_merchant(title)
        node_id = node_url.rsplit("/", 1)[-1] if node_url else None

        deals.append({
            "id": node_id,
            "source": "ozbargain",
            "title": title,
            "node_url": node_url,
            "merchant_url": merchant_url,
            "merchant": merchant,
            "price_aud": _parse_price_aud(title),
            "categories": categories,
            "expiry": expiry,
            "status": status,
            "click_count": click_count,
            "votes_pos": votes_pos,
            "votes_neg": votes_neg,
            "pubdate": (item.findtext("pubDate") or "").strip() or None,
            "program_hint": _program_hint(title, merchant, categories),
        })
    return deals


def fetch_deals(tag: str = "", limit: int = 40, timeout: float = 15.0) -> list[dict]:
    """Fetch the live OzBargain feed and parse it. `tag` -> /tag/<tag>/feed, else /deals/feed.
    Drops items already marked expired. Returns at most `limit` deals."""
    url = f"{OZB_BASE}/tag/{tag}/feed" if tag else f"{OZB_BASE}/deals/feed"
    resp = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout,
                     follow_redirects=True)
    resp.raise_for_status()
    deals = parse_feed(resp.content)
    deals = [d for d in deals if d["status"] != "expired"]
    return deals[:limit]
