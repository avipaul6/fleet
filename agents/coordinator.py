"""Root orchestrator. Sequential pipeline over a parallel scout fan-out.

Pattern: ParallelAgent(scouts) -> valuer -> worth_it -> caller -> presenter.
State flows via output_key/session state. Deployed as a Cloud Run service;
Cloud Scheduler -> Pub/Sub push triggers the nightly run.
"""
from google.adk.agents import SequentialAgent, ParallelAgent, Agent
from agents import model_factory
from agents.scouts import scout_ozbargain, scout_rewards, scout_stock
from agents.valuer import valuer
from agents.worth_it import worth_it
from agents.caller import caller

scout_fleet = ParallelAgent(
    name="scout_fleet",
    sub_agents=[scout_ozbargain, scout_rewards, scout_stock],
)

presenter = Agent(
    name="presenter",
    model=model_factory.fast(),
    instruction="""Compose the morning brief from valued offers, verdicts and
call results: max 5 ActionItems, ranked by net value. Each line: headline,
net $, verdict, one-sentence reasoning. Include what you REFUSED to do and
why — the human should always see the fleet's restraint, not just its wins.
Send via Gmail API tool.""",
    tools=[],  # TODO: gmail_send tool
    output_key="morning_brief",
)

root_agent = SequentialAgent(
    name="pointsduck",
    sub_agents=[scout_fleet, valuer, worth_it, caller, presenter],
)
