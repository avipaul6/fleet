"""Worth-It: the refusal engine. Computes door-to-door cost of the errand.

This agent saying 'skip it, not worth the drive' is a governance feature
expressed as a delightful product feature — and a demo beat.
"""
from google.adk.agents import Agent
from agents import model_factory
from config.settings import settings


def errand_cost(store_lat: float, store_lng: float) -> dict:
    """Tool: Google Maps Routes API (GCP) — drive time + distance from home.
    Returns full economics of the trip. TODO: wire Routes API client."""
    # minutes, km = routes_api(home -> store -> home)
    raise NotImplementedError


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
    instruction="""For each actionable in-store offer with stock: compute the
full door-to-door economics with your tools. If net_after_trip is negative,
verdict=skip and say WHY in one honest sentence ('22 min each way costs more
than the Ooshie is worth'). Saving the human a wasted Saturday is success.""",
    tools=[errand_cost, worth_it_verdict],
    output_key="verdicts",
)
