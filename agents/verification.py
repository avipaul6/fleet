"""Gated phone stock-verification — DuckFleet's 'meaningful action on your behalf'.

Every dial passes the gates: calling hours, one-call-per-store-per-day, explicit human
approval, and mandatory AI self-identification. The outbound line is synthesized with
REAL Cloud Text-to-Speech (a genuine audio artifact); the store's answer is clearly
LABELLED simulated until the live phone gateway (Dialogflow CX) is wired. Honesty > fakery.

Runtime-agnostic + deterministic (the gates are code, not model judgement); the caller
agent composes the question and consumes the transcript.
"""
from __future__ import annotations

import datetime
from pathlib import Path

from guardrails.gates import (gate_phone_call, gate_call_script, CALL_SCRIPT_PREAMBLE,
                              record, GateDenied)


def synthesize_audio(text: str, out_path: str) -> str | None:
    """Real Cloud Text-to-Speech → an audio file of exactly what the agent would say.
    Best-effort: returns the path, or None if TTS is unavailable (flow still proceeds)."""
    try:
        from google.cloud import texttospeech
        client = texttospeech.TextToSpeechClient()
        resp = client.synthesize_speech(
            input=texttospeech.SynthesisInput(text=text),
            voice=texttospeech.VoiceSelectionParams(
                language_code="en-AU", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE),
            audio_config=texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3),
        )
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_bytes(resp.audio_content)
        return out_path
    except Exception:
        return None


def run_verification_call(store_name: str, item: str, human_approved: bool, *,
                          calls_today: int = 0, local_hour: int | None = None,
                          out_dir: str = ".", simulated_answer: str = "In stock — a few left.") -> dict:
    """Full gated call flow. Returns a dict describing what happened (or why it was
    refused). A denial is a CORRECT outcome, not a failure."""
    local_hour = local_hour if local_hour is not None else datetime.datetime.now().hour

    # Gate 1: call policy (hours / one-per-store / human approval).
    try:
        gate_phone_call(store_name, calls_today, local_hour, human_approved)
    except GateDenied as e:
        return {"status": "refused", "reason": str(e), "store": store_name}

    # Compose the question — MUST open with AI self-identification (Gate 2 enforces it).
    question = CALL_SCRIPT_PREAMBLE + f"do you currently have {item} in stock?"
    gate_call_script(question)

    # Real TTS audio of the agent's line (labelled simulation until live telephony).
    safe = "".join(c if c.isalnum() else "_" for c in store_name).lower()
    audio_path = synthesize_audio(question, f"{out_dir}/call_{safe}.mp3")

    ref = record("call_placed", store=store_name, item=item, simulated=True)
    return {
        "status": "completed", "simulated": True, "store": store_name,
        "script": question, "audio_path": audio_path,
        "answer": simulated_answer, "audit_ref": ref,
    }
