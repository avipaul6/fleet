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


def compute_stack_value(price_aud: float, points_out: int, program: str,
                        multipliers: list[float]) -> dict:
    """Tool: deterministic stack math. The LLM finds the stack; python does
    the arithmetic (never let the model do the maths it can delegate)."""
    total_points = points_out
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
    instruction="""You are a points-value analyst. Given normalised Offers:
1. Detect stacks: sale price x card multiplier x program boost on the SAME purchase.
2. Call compute_stack_value for every candidate — never do arithmetic yourself.
3. Set tos_risk: 'grey' for anything relying on repeated-redemption loopholes,
   'violation' for anything breaching program T&Cs. Be conservative.
4. Rank by net_value_aud and emit JSON. A stack under 1.0c/pt for Qantas is
   duck-tier: flag it loudly.""",
    tools=[compute_stack_value],
    output_key="valued_offers",
)
