"""Root orchestrator. Sequential pipeline over a parallel scout fan-out.

Pattern: ParallelAgent(scouts) -> valuer -> worth_it -> caller -> presenter.
State flows via output_key/session state. Deployed as a Cloud Run service;
Cloud Scheduler -> Pub/Sub push triggers the nightly run.
"""
from google.adk.agents import SequentialAgent, ParallelAgent
from agents.scouts import scout_ozbargain, scout_rewards, scout_stock
from agents.valuer import valuer
from agents.worth_it import worth_it
from agents.caller import caller
from agents.presenter import presenter

scout_fleet = ParallelAgent(
    name="scout_fleet",
    sub_agents=[scout_ozbargain, scout_rewards, scout_stock],
)

root_agent = SequentialAgent(
    name="duckfleet",
    sub_agents=[scout_fleet, valuer, worth_it, caller, presenter],
)
