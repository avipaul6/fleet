#!/usr/bin/env python3
"""
DuckFleet — GCP architecture diagram (mingrammer/diagrams).

Renders official Google Cloud icons for the nightly governed agent fleet.
Mirrors docs/architecture.svg; regenerate whenever the SVG changes.

Setup (one-time):
    brew install graphviz          # the `dot` renderer (required)
    python3 -m venv .venv && source .venv/bin/activate
    pip install diagrams

Run:
    python demo/gcp-hackathon/architecture_diagram.py
    # -> writes duckfleet_architecture.png next to this script

Notes on icons:
  - Real GCP icons: Scheduler, Build, Cloud Run, Vertex AI, Maps Routes,
    Text-to-Speech, Secret Manager, BigQuery, Cloud Logging.
  - Twilio uses the official Twilio icon (saas) — it's the one non-GCP service.
  - Artifact Registry -> ContainerRegistry icon (closest match; label is correct).
  - Gmail API + Google Calendar have no icons in `diagrams`; shown as labelled
    blank nodes. To get real logos, swap them for diagrams.custom.Custom with a
    downloaded PNG (see the commented example at the bottom).
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.gcp.devtools import Scheduler, Build, ContainerRegistry
from diagrams.gcp.compute import Run
from diagrams.gcp.ml import VertexAI, TextToSpeech
from diagrams.gcp.network import Routes
from diagrams.gcp.security import SecretManager
from diagrams.gcp.analytics import BigQuery
from diagrams.gcp.operations import Logging
from diagrams.saas.communication import Twilio
from diagrams.custom import Custom

import os

ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")

graph_attr = {
    "fontsize": "20",
    "bgcolor": "#f8f9fa",
    "pad": "0.6",
    "splines": "ortho",   # rectangular right-angle edges, GCP-diagram style
    "nodesep": "0.6",
    "ranksep": "1.1",
}

with Diagram(
    "DuckFleet — Governed Agent Fleet on Google Cloud",
    filename="duckfleet_architecture",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    outformat="png",  # change to "svg" for a crisp vector version
):

    # ① nightly trigger
    scheduler = Scheduler("Cloud Scheduler\n02:00 Australia/Brisbane")

    # build & deploy
    with Cluster("Build & Deploy"):
        build = Build("Cloud Build\nsource -> image")
        registry = ContainerRegistry("Artifact Registry\ncontainer image")
        build >> Edge(color="#5f6368") >> registry

    # ② the fleet — one Cloud Run Job, six agents in sequence
    with Cluster("Cloud Run Job · duckfleet-nightly — the fleet (Google ADK)"):
        scouts = Run("Scouts\nOzBargain -> offers")
        valuer = Run("Valuer\nstack maths, cpp")
        guardrails = Run("Guardrails\nToS · cap · prefs · audit")
        worth_it = Run("Worth-It\ndrive vs value · refuses")
        presenter = Run("Presenter\nranked brief + ROI")
        caller = Run("Caller · gated\nverify stock by phone")
        scouts >> valuer >> guardrails >> worth_it >> presenter >> caller

    # ② services the fleet calls
    with Cluster("Google Cloud services used by the fleet"):
        vertex = VertexAI("Vertex AI\nGemini (per tier)")
        maps = Routes("Maps Routes API\ndrive time & distance")
        tts = TextToSpeech("Text-to-Speech\ngated call audio")
        secrets = SecretManager("Secret Manager\nGmail + Twilio creds")

    # ③ outputs — state, audit, delivery
    with Cluster("State, audit & delivery (outputs)"):
        bq = BigQuery("BigQuery\noffer_history")
        logging = Logging("Cloud Logging\ngovernance audit trail")
        gmail = Custom("Gmail API\nmorning brief", os.path.join(ICON_DIR, "gmail.png"))
        calendar = Custom("Google Calendar\nreminder links", os.path.join(ICON_DIR, "calendar.png"))

    twilio = Twilio("Twilio\ngated call · non-GCP")

    # onboarding input
    onboarding = VertexAI("Onboarding agent\nchat -> profile.json")

    # ---- wiring ----
    scheduler >> Edge(color="#4285F4") >> scouts
    registry >> Edge(color="#5f6368", style="dashed", label="deploy") >> scouts

    onboarding >> Edge(color="#5f6368", style="dashed", label="profile.json") >> scouts

    # fleet uses services
    valuer >> Edge(color="#9aa0a6", style="dotted") >> vertex
    worth_it >> Edge(color="#9aa0a6", style="dotted") >> maps
    caller >> Edge(color="#9aa0a6", style="dotted") >> tts
    caller >> Edge(color="#9aa0a6", style="dotted") >> secrets

    # fleet writes outputs
    presenter >> Edge(color="#34A853") >> bq
    guardrails >> Edge(color="#EA4335") >> logging
    presenter >> Edge(color="#34A853") >> gmail
    presenter >> Edge(color="#4285F4") >> calendar
    caller >> Edge(color="#FBBC04") >> twilio


# ----------------------------------------------------------------------------
# Want the real Gmail / Calendar logos? Download PNGs and use Custom nodes:
#
#   from diagrams.custom import Custom
#   gmail = Custom("Gmail API\nmorning brief", "./icons/gmail.png")
#   calendar = Custom("Google Calendar\nreminder links", "./icons/calendar.png")
#
# (Grab icons from Google's brand resources; keep them in demo/.../icons/.)
# ----------------------------------------------------------------------------
