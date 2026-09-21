from pathlib import Path
import traceback

root = Path(r"C:\Users\twent\Desktop\jarvis-voice-butler")
src = root / "jarvis_new" / "src"
agent = src / "agent.py"
print("agent exists", agent.is_file(), "bytes", agent.stat().st_size if agent.is_file() else 0)
print("--- bats ---")
for p in list(root.glob("*.bat")) + list(root.glob("*start*.bat")):
    print(p)
print("--- compile ---")
try:
    compile(agent.read_text(encoding="utf-8"), str(agent), "exec")
    print("syntax OK")
except Exception:
    traceback.print_exc()
print("--- imports ---")
text = agent.read_text(encoding="utf-8")
for needle in ("lk_openai", "with_ollama", "RealtimeModel", "stt=inference", "tts=inference", "from livekit.plugins"):
    print(needle, "YES" if needle in text else "NO")
print("--- llm block ---")
lines = text.splitlines()
for i, line in enumerate(lines, 1):
    if 1 <= i <= 30 or 48 <= i <= 75 or 90 <= i <= 125:
        print(f"{i:4}|{line}")
