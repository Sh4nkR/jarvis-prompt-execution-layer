#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(r"C:\Users\twent\Desktop\jarvis-voice-butler")
SRC = ROOT / "jarvis_new" / "src"
prompts = SRC / "prompts.py"
if not prompts.is_file():
    raise SystemExit("prompts.py not found")

text = prompts.read_text(encoding="utf-8")
save = SRC / "prompts.py.pre_strip"
if not save.exists():
    save.write_text(text, encoding="utf-8")
    print("backup", save)

before = text
text, n = re.subn(
    r"\n[ \t]*# Guardrails[\s\S]*?(?=\n[ \t]*# [A-Za-z]|\n[ \t]*\"\"\")",
    "\n",
    text,
    count=1,
)
print("guardrails block removed:", n)

line_re = re.compile(
    r"^(?=.*(?:decline harmful|Stay within safe, lawful|out-of-scope requests|"
    r"I cannot help|as an AI language model|I must refuse|safety guidelines)).*$\n",
    re.I | re.M,
)
text, n2 = line_re.subn("", text)
print("refusal lines removed:", n2)

add = (
    "    - Do not lecture or moralize. Stay a dry British butler.\n"
    "    - Execute the request. Keep replies short.\n"
)
if "Do not lecture or moralize" not in text:
    idx = text.rfind('"""')
    if idx == -1:
        raise SystemExit("no closing quotes")
    text = text[:idx] + add + text[idx:]
    print("added two butler lines")

prompts.write_text(text, encoding="utf-8")
print("prompts.py", len(before), "->", len(text))

cleared = 0
for mem in ROOT.rglob("memory.md"):
    raw = mem.read_text(encoding="utf-8", errors="replace")
    bak = mem.with_name(mem.name + ".bak")
    if not bak.exists():
        bak.write_text(raw, encoding="utf-8")
    mem.write_text("# Memory\n", encoding="utf-8")
    print("cleared", mem)
    cleared += 1
print("memory files cleared:", cleared)
print("DONE. close.bat then start.bat")
