"""The contract every scout must emit. Locking this early is 80% of the build."""
from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class Offer(BaseModel):
    id: str
    source: Literal["pointhacks", "ozbargain", "everyday_rewards", "flybuys", "manual"]
    source_url: str
    merchant: str
    program: Literal["qantas_ff", "velocity", "flybuys", "everyday_rewards"]
    offer_type: Literal["bonus_points", "multiplier", "discount_stack", "collectible"]
    item: str | None = None            # "rubber duck", "ooshie"
    price_aud: float | None = None
    points_out: int | None = None
    spend_required_aud: float | None = None
    stackable_with: list[str] = []     # other offer ids
    expiry: datetime | None = None
    scraped_at: datetime
    requires_instore: bool = False
    tos_risk: Literal["none", "grey", "violation"] = "none"  # valuer sets this


class StockSignal(BaseModel):
    offer_id: str
    store_name: str
    store_lat: float
    store_lng: float
    phone: str | None = None
    online_stock_state: Literal["in_stock", "low", "out", "unknown"]
    last_verified: datetime | None = None   # stale -> caller agent may escalate


class ActionItem(BaseModel):
    """What the presenter puts in the morning brief."""
    rank: int
    headline: str                      # "20 ducks @ BigW Mt Gravatt = 0.59c/pt"
    net_value_aud: float               # value minus money, fuel, and time cost
    cents_per_point: float | None = None
    verdict: Literal["do_it", "needs_approval", "skip"]
    reasoning: str                     # shown to the human — always explain
    audit_ref: str                     # Cloud Logging trace id
