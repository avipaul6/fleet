"""Scout fleet: parallel ingestion agents. FAST model tier.

Hackathon cut: 2 live scrapers + 1 fixture-backed scout is plenty.
Scrapers are read-only, rate-limited, robots.txt-respecting — say so in the video.
"""
from google.adk.agents import Agent
from agents import model_factory, ozbargain_feed
from schemas.offer import Offer  # noqa: F401  (schema is the output contract)


def fetch_ozbargain_deals(tag: str = "", limit: int = 40) -> list[dict]:
    """Tool: fetch + parse the live OzBargain deal feed (read-only, rate-limited,
    robots-respecting). `tag` narrows to /tag/<tag>/feed; empty = the main deals feed.
    Returns raw deal dicts (id, title, merchant, price_aud, categories, program_hint,
    …); the agent normalises these into Offer objects and filters to the user's
    programs. Deterministic scrape logic lives in agents/ozbargain_feed.py."""
    return ozbargain_feed.fetch_deals(tag=tag, limit=limit)


def fetch_everyday_rewards_boosts() -> list[dict]:
    """Tool: current Everyday Rewards boost offers. TODO: fixture for demo."""
    raise NotImplementedError


def check_online_stock(product_url: str, postcode: str) -> dict:
    """Tool: per-store availability from retailer product page. Returns
    StockSignal-shaped dict incl. last_verified so the caller agent can
    decide whether online data is stale enough to warrant a phone call."""
    raise NotImplementedError


SCOUT_INSTRUCTION = """You are a deal scout. Use your tools to fetch current offers,
then emit ONLY a JSON array of Offer objects matching the provided schema.
Never invent offers. If a field is unknown, use null. Mark anything that smells
like ToS abuse (mass account creation, coupon exploits) with tos_risk."""

scout_ozbargain = Agent(
    name="scout_ozbargain",
    model=model_factory.fast(),
    instruction=SCOUT_INSTRUCTION,
    tools=[fetch_ozbargain_deals],
    output_key="offers_ozbargain",
)

scout_rewards = Agent(
    name="scout_rewards",
    model=model_factory.fast(),
    instruction=SCOUT_INSTRUCTION,
    tools=[fetch_everyday_rewards_boosts],
    output_key="offers_rewards",
)

scout_stock = Agent(
    name="scout_stock",
    model=model_factory.fast(),
    instruction="For each in-store offer, check per-store stock near the user's "
                "home and emit StockSignal JSON. Note last_verified timestamps.",
    tools=[check_online_stock],
    output_key="stock_signals",
)
