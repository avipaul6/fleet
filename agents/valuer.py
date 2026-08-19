"""Valuer: the money feature. STRONG model tier.

Finds stacks across offers and computes cents-per-point. This is the agent
that looks at a $3.50 duck and sees a business-class seat.
"""
from google.adk.agents import Agent
from agents import model_factory

# Redemption benchmarks (cents per point of realisable value). Keep in
# Firestore in prod; constants are fine for the demo.
REDEMPTION_VALUE_CPP = {"qantas_ff": 1.8, "velocity": 1.7, "flybuys": 0.5,
                        "everyday_rewards": 0.5}


def compute_stack_value(price_aud: float, points_out: int = 0, program: str = "none",
                        multipliers: list[float] | None = None) -> dict:
    """Tool: deterministic stack math. The LLM finds the stack; python does
    the arithmetic (never let the model do the maths it can delegate).
    points_out = points from the offer itself; multipliers = program/card boosts
    applied on the same purchase (e.g. [10.0, 2.0])."""
    multipliers = multipliers or []
    total_points = int(points_out or 0)
    for m in multipliers:
        total_points = int(total_points * m)
    cpp_cost = (price_aud / total_points) * 100 if total_points else float("inf")
    cpp_value = REDEMPTION_VALUE_CPP.get(program, 0.5)
    return {
        "total_points": total_points,
        "cost_cents_per_point": round(cpp_cost, 2),
        "value_multiple": round(cpp_value / cpp_cost, 2) if cpp_cost else 0,
        "net_value_aud": round(total_points * cpp_value / 100 - price_aud, 2),
    }


valuer = Agent(
    name="valuer",
    model=model_factory.strong(),
    instruction="""You are DuckFleet's points-value analyst. You are given a JSON array of
offers; each may include `points_out` (points from the offer) and a `multipliers` array
(program/card boosts that stack on the same purchase).

For EACH offer:
1. If it has a points angle (points_out > 0), call compute_stack_value(price_aud,
   points_out, program, multipliers) — NEVER do the arithmetic yourself.
2. If it has no points angle (no points_out and no multipliers), do NOT invent numbers —
   mark it "no_points_angle" with null value fields.
3. Set tos_risk conservatively: 'grey' for repeated-redemption / multi-account loopholes,
   'violation' for T&C breaches, else 'none'.

Emit ONLY a JSON array (no prose, no markdown fences), ranked by net_value_aud descending
(no_points_angle offers last). Each element:
  {id, merchant, program, total_points, cost_cents_per_point, net_value_aud,
   value_multiple, tos_risk, note}
In `note`, call out duck-tier finds loudly (a Qantas stack under ~1c/point is a duck).""",
    tools=[compute_stack_value],
    output_key="valued_offers",
)
