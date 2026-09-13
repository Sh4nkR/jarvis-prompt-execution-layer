"""Create an ElevenLabs instant clone from workspace/my_voice.wav (your voice only)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(".env.local")

ADD_VOICE = "https://api.elevenlabs.io/v1/voices/add"


def main() -> int:
    key = (os.getenv("ELEVEN_API_KEY") or "").strip()
    if not key:
        print("Set ELEVEN_API_KEY in .env.local")
        return 1
    wav = Path(sys.argv[1] if len(sys.argv) > 1 else "workspace/my_voice.wav")
    if not wav.is_file():
        print(f"Missing sample: {wav}")
        print("Put a short clip of YOUR voice there (clean speech, no music).")
        return 1
    name = sys.argv[2] if len(sys.argv) > 2 else "jarvis-clone"
    with wav.open("rb") as f:
        resp = httpx.post(
            ADD_VOICE,
            headers={"xi-api-key": key},
            data={"name": name},
            files={"files": (wav.name, f, "audio/wav")},
            timeout=120.0,
        )
    if resp.status_code >= 400:
        print(resp.status_code, resp.text)
        return 1
    voice_id = resp.json().get("voice_id")
    print("voice_id=", voice_id)
    print("Put that in ELEVENLABS_VOICE_ID and set USE_CLONED_VOICE=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
