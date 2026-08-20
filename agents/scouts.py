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

OZB_SCOUT_INSTRUCTION = """You are DuckFleet's OzBargain scout. The user chases loyalty
points across these programs: qantas_ff, velocity, flybuys, everyday_rewards.

STEP 1 — call fetch_ozbargain_deals() to get raw live deals (each has: id, title,
merchant, merchant_url, node_url, price_aud, categories, program_hint, requires-instore
cues in the title, votes).

STEP 2 — KEEP only deals with a plausible points angle: a program_hint is set, OR the
merchant earns a scheme (Coles->flybuys, Woolworths/BigW->everyday_rewards), OR it's a
credit-card / frequent-flyer / bonus-points offer, OR a strong stackable discount at a
points-earning retailer. DROP generic bargains with no points angle.

STEP 3 — emit ONLY a JSON array (no prose, no markdown fences) of Offer objects:
  id           = the deal id (string)
  source       = "ozbargain"
  source_url    = merchant_url if present, else node_url
  merchant     = the merchant
  program      = program_hint if set; else infer from categories/title; else "none"
  offer_type   = one of bonus_points | multiplier | discount_stack | collectible (closest fit)
  category     = one of credit_card | insurance | energy | telco | groceries |
                 subscription | collectible | shopping | other (infer from tags/merchant/title;
                 a card is credit_card even if it earns points; health/car/home cover is insurance)
  item         = short item name, or null
  price_aud    = the price, or null
  points_out   = points earned ONLY if the deal states it, else null
  spend_required_aud = minimum spend if stated, else null
  stackable_with = []
  requires_instore = true if the title implies in-store / C&C / limited stores
  tos_risk     = "grey" if it leans on coupon-stacking / multi-account / repeated
                 redemption; "violation" if clearly breaching T&Cs; else "none"
Never invent deals. If nothing qualifies, output []."""

scout_ozbargain = Agent(
    name="scout_ozbargain",
    model=model_factory.fast(),
    instruction=OZB_SCOUT_INSTRUCTION,
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
