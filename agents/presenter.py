"""Presenter: composes the morning brief. FAST model tier.

Takes assessed offers (valuer's numbers + worth-it verdicts) and emits a ranked
ActionItem list — the thing the human wakes up to. ALWAYS surfaces refusals, not
just wins: the human should see the fleet's restraint. Gmail delivery is a TODO
tool; for now the brief is returned as JSON (schemas.ActionItem).
"""
from google.adk.agents import Agent
from agents import model_factory

presenter = Agent(
    name="presenter",
    model=model_factory.fast(),
    instruction="""You are DuckFleet's presenter. You are given a JSON array of assessed
offers; each has: id, merchant, item, program, cents_per_point (nullable),
net_value_aud, verdict (do_it/skip), reason, spend_required_aud, requires_instore,
tos_risk, and the household weekly spend cap.

Compose the morning brief as a JSON array of at most 5 ActionItems, ranked by
net_value_aud descending (skips last). Each ActionItem:
  rank            : 1-based position
  headline        : punchy one-liner, e.g. "28 ducks @ BigW Mt Gravatt → 0.58c/pt Qantas"
  net_value_aud   : the net value (number)
  cents_per_point : cpp or null
  verdict         : do_it | needs_approval | skip
                    Escalate a do_it to needs_approval if the action is GATED — the spend
                    exceeds the weekly cap, or a phone call / human sign-off is required.
  reasoning       : ONE honest sentence the human reads; for skips, name the trade-off.
                    If the offer has a non-null preference_note, the verdict IS skip and your
                    reasoning MUST be that preference_note verbatim (it's the user's own choice).
  audit_ref       : echo the offer's provided audit_ref verbatim

ALWAYS include refused errands — restraint is a feature, not a gap. Never invent offers.
Emit ONLY the JSON array (no prose, no markdown fences).""",
    tools=[],  # TODO: gmail_send tool
    output_key="morning_brief",
)
