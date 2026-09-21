#!/usr/bin/env python3
from pathlib import Path
import re, shutil

SRC = Path(r"C:\Users\twent\Desktop\jarvis-voice-butler\jarvis_new\src")
agent = SRC / "agent.py"
if not agent.is_file():
    raise SystemExit("agent.py not found")

bak = SRC / "agent.py.gemini-bak"
if not bak.exists():
    shutil.copyfile(agent, bak)
    print("backup", bak)

text = agent.read_text(encoding="utf-8")

if "as lk_openai" not in text:
    old = "from livekit.plugins import ai_coustics, google"
    if old in text:
        text = text.replace(old, old + ", openai as lk_openai", 1)
    else:
        text = "from livekit.plugins import openai as lk_openai\n" + text

if "with_ollama" not in text:
    text2, n = re.subn(
        r"\s*llm=google\.beta\.realtime\.RealtimeModel\([\s\S]*?\),",
        "\n            llm=lk_openai.LLM.with_ollama(\n                model=\"dolphin3:8b\",\n                base_url=\"http://127.0.0.1:11434/v1\",\n            ),",
        text,
        count=1,
    )
    if n == 0:
        raise SystemExit("RealtimeModel not found")
    text = text2
    print("swapped Gemini Live -> dolphin3:8b")

text = re.sub(
    r"^(\s*)#\s*(stt=inference\.STT\([^\n]*\),)",
    r"\1\2",
    text,
    count=1,
    flags=re.M,
)

out = []
u = False
for line in text.splitlines(True):
    if re.match(r"^\s*#\s*tts=inference\.TTS\(", line):
        line = re.sub(r"^(\s*)#\s?", r"\1", line, count=1)
        u = ")" not in line
    elif u:
        if re.match(r"^\s*#", line):
            line = re.sub(r"^(\s*)#\s?", r"\1", line, count=1)
        if ")" in line:
            u = False
    out.append(line)
text = "".join(out)

if "stt=inference.STT" not in text:
    text = text.replace(
        "session = AgentSession(",
        'session = AgentSession(\n        stt=inference.STT(model="deepgram/nova-3", language="en"),\n        tts=inference.TTS(model="cartesia/sonic-3"),',
        1,
    )
    print("inserted STT/TTS")

agent.write_text(text, encoding="utf-8")
print("DONE")
