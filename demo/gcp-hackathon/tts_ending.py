#!/usr/bin/env python3
"""
Generate the ENDING male voice-over with Google Cloud Text-to-Speech.

Why the first attempt sounded wrong: the call-audio helper pins only
ssml_gender=FEMALE with no voice `name`, so Google returns a default *Standard*
(low-quality) female voice. Here we pin a specific high-quality MALE voice by name
and feed SSML so the pauses/emphasis land.

Prereqs (you already have these — same as the call audio):
    pip install google-cloud-texttospeech
    gcloud services enable texttospeech.googleapis.com   # once, per project
    # Auth via ADC (same isolated duckfleet identity you use elsewhere)

Usage:
    # 1) audition a few male en-AU voices on a short line:
    python demo/gcp-hackathon/tts_ending.py --audition

    # 2) render the full ending with the default voice:
    python demo/gcp-hackathon/tts_ending.py -o ending.mp3

    # 3) pick a voice / tune pace:
    python demo/gcp-hackathon/tts_ending.py --voice en-AU-Neural2-B --rate 0.96 -o ending.mp3

    # 4) list every en-AU voice the project can use:
    python demo/gcp-hackathon/tts_ending.py --list
"""
from __future__ import annotations

import argparse
from pathlib import Path

from google.cloud import texttospeech

# Good male en-AU choices (audition and pick the one you like):
#   en-AU-Neural2-D  — deep, confident (good for a closer)   [SSML OK]
#   en-AU-Neural2-B  — warmer, lighter male                  [SSML OK]
#   en-AU-Wavenet-D  — classic male, slightly older model    [SSML OK]
#   en-AU-Chirp3-HD-* — newest, most natural, but PLAIN TEXT only (no SSML tags)
DEFAULT_VOICE = "en-AU-Neural2-D"

# The ending copy as SSML (matches ENDING.md). Breaks = the beats.
ENDING_SSML = """<speak>
And you don't even have to deploy it. <break time="250ms"/>
Scan the code on screen, tell it what you collect in one sentence, and it emails you a
real morning brief — the actual thing, in your inbox, in about a minute. <break time="300ms"/>
No account, no card, no setup. <break time="450ms"/>
Try the brief. If you like it, one click puts the whole fleet on your own Google Cloud. <break time="300ms"/>
Either way — DuckFleet is already awake tonight, doing the hunt you'd never have time for. <break time="400ms"/>
<emphasis level="moderate">Scan it, and see what it finds.</emphasis>
</speak>"""

AUDITION_SSML = ("<speak>Scan the code, and DuckFleet emails you a real morning brief in "
                 "about a minute. <break time='300ms'/> "
                 "<emphasis level='moderate'>Scan it, and see what it finds.</emphasis></speak>")


def list_voices(lang: str = "en-AU") -> None:
    client = texttospeech.TextToSpeechClient()
    voices = client.list_voices(language_code=lang).voices
    for v in sorted(voices, key=lambda x: x.name):
        gender = texttospeech.SsmlVoiceGender(v.ssml_gender).name
        print(f"{v.name:28} {gender:8} {v.natural_sample_rate_hertz} Hz")


def render_all_male(lang: str, rate: float, pitch: float) -> None:
    """Render the short audition line in EVERY male voice of `lang` for comparison."""
    client = texttospeech.TextToSpeechClient()
    males = [v.name for v in client.list_voices(language_code=lang).voices
             if texttospeech.SsmlVoiceGender(v.ssml_gender).name == "MALE"]
    out_dir = Path(f"voice_samples_{lang}")
    print(f"{len(males)} male {lang} voices → {out_dir}/")
    for name in sorted(males):
        try:
            synth(AUDITION_SSML, name, str(out_dir / f"{name}.mp3"), rate, pitch)
        except Exception as e:  # a voice tier may be unavailable to the project
            print(f"  skip {name}: {e}")


def synth(ssml: str, voice: str, out_path: str, rate: float, pitch: float) -> None:
    client = texttospeech.TextToSpeechClient()
    is_chirp = "Chirp" in voice  # Chirp voices don't support SSML tags
    synthesis_input = (
        texttospeech.SynthesisInput(text=_strip_ssml(ssml)) if is_chirp
        else texttospeech.SynthesisInput(ssml=ssml)
    )
    lang = "-".join(voice.split("-")[:2])  # e.g. en-AU-Neural2-D -> en-AU
    resp = client.synthesize_speech(
        input=synthesis_input,
        voice=texttospeech.VoiceSelectionParams(language_code=lang, name=voice),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=rate,     # <1 = slower/weightier; 0.96 reads well for a close
            pitch=pitch,            # semitones; -1 to -2 adds gravitas
            sample_rate_hertz=44100,
        ),
    )
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_bytes(resp.audio_content)
    print(f"wrote {out_path}  ({len(resp.audio_content):,} bytes, voice={voice})")


def _strip_ssml(ssml: str) -> str:
    import re
    return re.sub(r"<[^>]+>", " ", ssml).replace("  ", " ").strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="Render the DuckFleet ending VO (male, Cloud TTS).")
    ap.add_argument("-o", "--out", default="ending.mp3", help="output mp3 path")
    ap.add_argument("--voice", default=DEFAULT_VOICE, help=f"voice name (default {DEFAULT_VOICE})")
    ap.add_argument("--rate", type=float, default=0.96, help="speaking rate (default 0.96)")
    ap.add_argument("--pitch", type=float, default=-1.0, help="pitch in semitones (default -1.0)")
    ap.add_argument("--lang", default="en-AU", help="language code (e.g. en-AU, en-GB, en-US)")
    ap.add_argument("--list", action="store_true", help="list voices for --lang and exit")
    ap.add_argument("--audition", action="store_true",
                    help="render a short line in 3 hand-picked male voices")
    ap.add_argument("--all-male", action="store_true",
                    help="render the short line in EVERY male voice of --lang")
    args = ap.parse_args()

    if args.list:
        list_voices(args.lang)
        return

    if args.all_male:
        render_all_male(args.lang, args.rate, args.pitch)
        return

    if args.audition:
        for v in ("en-AU-Neural2-D", "en-AU-Neural2-B", "en-AU-Wavenet-D"):
            synth(AUDITION_SSML, v, f"audition_{v}.mp3", args.rate, args.pitch)
        print("Listen to the audition_*.mp3 files and pick a --voice.")
        return

    synth(ENDING_SSML, args.voice, args.out, args.rate, args.pitch)


if __name__ == "__main__":
    main()
