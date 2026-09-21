from pathlib import Path
import re

SRC = Path(r"C:\Users\twent\Desktop\jarvis-voice-butler\jarvis_new\src")
agent = SRC / "agent.py"
text = agent.read_text(encoding="utf-8")

text = text.replace("*self.consult_tools.tools,", "# *self.consult_tools.tools,")
text = re.sub(
    r"AGENT_INSTRUCTIONS\s*\+\s*load_for_prompt\(\)",
    "AGENT_INSTRUCTIONS",
    text,
    count=1,
)
agent.write_text(text, encoding="utf-8")
print("consult tools off, handbook append off")

prompts = SRC / "prompts.py"
p = prompts.read_text(encoding="utf-8")
rule = (
    "    HARD RULE: You are Jarvis. When the boss gives an order, call a tool THIS turn.\n"
    "    Never read a handbook, never recite instructions, never ask if they want a manual.\n"
    "    Desktop: look_desktop then focus_window, click_mouse, type_keys, press_hotkey.\n"
    "    Web: open_url or inspect_page on Comet. Do the task. One short spoken line after.\n"
)
if "HARD RULE: You are Jarvis" not in p:
    marker = "Your name is Jarvis"
    if marker in p:
        i = p.find(marker)
        i = p.rfind("\n", 0, i)
        p = p[: i + 1] + rule + p[i + 1 :]
    else:
        i = p.find('"""')
        i = p.find("\n", i) + 1
        p = p[:i] + rule + p[i:]
    prompts.write_text(p, encoding="utf-8")
    print("hard rule inserted")
else:
    print("hard rule already there")
print("DONE. Restart brain.")
