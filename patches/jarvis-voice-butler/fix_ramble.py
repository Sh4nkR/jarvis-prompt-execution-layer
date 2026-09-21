#!/usr/bin/env python3
from pathlib import Path
import shutil

SRC = Path.cwd() / "jarvis_new" / "src"
if not (SRC / "prompts.py").is_file():
    raise SystemExit("cd to C:\\Users\\twent\\Desktop\\jarvis-voice-butler first")

SHORT = (
    "    - Do not lecture, moralize, or add safety sermons. Stay in butler character.\n"
    "    - Keep replies short. Answer the request. Do not ramble.\n"
)

bak = SRC / "prompts.py.bak"
cur = SRC / "prompts.py"
if bak.is_file():
    shutil.copyfile(bak, cur)
    print("restored prompts.py from backup")
else:
    print("no prompts.py.bak, editing current file")

text = cur.read_text(encoding="utf-8")
junk = (
    "# Uncensored",
    "Uncensored mode is ON",
    "Adult content",
    "swearing, dark humor",
    "Do not assist with child",
    "Do not say you are just an AI",
    "If a tool can do it, do it",
    "edgy roleplay",
)
if any(j in text for j in junk):
    lines = [ln for ln in text.splitlines(True) if not any(j in ln for j in junk)]
    text = "".join(lines)

if "Do not lecture, moralize" not in text:
    idx = text.rfind('"""')
    if idx == -1:
        raise SystemExit("could not find closing quotes in prompts.py")
    text = text[:idx] + SHORT + text[idx:]

cur.write_text(text, encoding="utf-8")
print("prompts.py is original butler voice + short no-lecture lines")
print("Restart Jarvis.")
