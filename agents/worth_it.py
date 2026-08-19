"""Worth-It: the refusal engine. Computes door-to-door cost of the errand.

This agent saying 'skip it, not worth the drive' is a governance feature
expressed as a delightful product feature — and a demo beat.
"""
import httpx
import google.auth
from google.auth.transport.requests import Request as _GAuthRequest

from google.adk.agents import Agent
from agents import model_factory
from config.settings import settings

_ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"


def _adc_bearer() -> str:
    """ADC access token for the isolated duckfleet identity — no key file."""
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(_GAuthRequest())
    return creds.token


def errand_cost(store_lat: float, store_lng: float) -> dict:
    """Tool: real door-to-door drive economics via Google Maps Routes API (GCP),
    authed with ADC. Computes home -> store one-way and doubles it for the round
    trip. Returns round-trip minutes + km (what worth_it_verdict needs)."""
    body = {
        "origin": {"location": {"latLng": {"latitude": settings.home_lat,
                                           "longitude": settings.home_lng}}},
        "destination": {"location": {"latLng": {"latitude": store_lat,
                                                "longitude": store_lng}}},
        "travelMode": "DRIVE",
    }
    headers = {
        "Authorization": f"Bearer {_adc_bearer()}",
        "X-Goog-User-Project": settings.project_id,
        "Content-Type": "application/json",
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
    }
    resp = httpx.post(_ROUTES_URL, json=body, headers=headers, timeout=15.0)
    resp.raise_for_status()
    route = resp.json()["routes"][0]
    one_way_km = route["distanceMeters"] / 1000
    one_way_min = int(str(route["duration"]).rstrip("s")) / 60
    return {
        "minutes": round(one_way_min * 2, 1),   # round trip
        "km": round(one_way_km * 2, 1),
        "one_way_minutes": round(one_way_min, 1),
        "one_way_km": round(one_way_km, 1),
    }


def worth_it_verdict(net_value_aud: float, minutes: float, km: float) -> dict:
    time_cost = (minutes / 60) * settings.time_value_aud_per_hour
    fuel_cost = km * settings.fuel_aud_per_km
    net = net_value_aud - time_cost - fuel_cost
    return {"trip_cost_aud": round(time_cost + fuel_cost, 2),
            "net_after_trip_aud": round(net, 2),
            "verdict": "do_it" if net > 0 else "skip"}


worth_it = Agent(
    name="worth_it",
    model=model_factory.fast(),
    instruction="""You are DuckFleet's worth-it gate. You are given a JSON array of
candidate errands; each has: id, merchant, net_value_aud (from the valuer), store_lat,
store_lng.

For EACH errand:
1. Call errand_cost(store_lat, store_lng) for the real drive minutes + km.
2. Call worth_it_verdict(net_value_aud, minutes, km). NEVER do the arithmetic yourself.

Emit ONLY a JSON array (no prose, no fences), each element:
  {id, merchant, trip_cost_aud, net_after_trip_aud, verdict, reason}
For verdict=skip, `reason` is ONE honest sentence naming the trade-off
('30 min round trip costs more than a $6 Ooshie is worth'). Saving the human a
wasted Saturday is a WIN, not a failure — say so plainly.""",
    tools=[errand_cost, worth_it_verdict],
    output_key="verdicts",
)
