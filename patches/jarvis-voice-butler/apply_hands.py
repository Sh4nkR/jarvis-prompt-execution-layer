from pathlib import Path
import shutil
import urllib.request

ROOT = Path(r"C:\Users\twent\Desktop\jarvis-voice-butler")
SRC = ROOT / "jarvis_new" / "src"
BASE = "https://raw.githubusercontent.com/Sh4nkR/jarvis-prompt-execution-layer/main/patches/jarvis-voice-butler/"

for name in ("desk_tools.py", "comet_attach.py"):
    dest = SRC / name
    urllib.request.urlretrieve(BASE + name, dest)
    print("wrote", dest)

agent = SRC / "agent.py"
text = agent.read_text(encoding="utf-8")
bak = SRC / "agent.py.pre_hands"
if not bak.exists():
    shutil.copyfile(agent, bak)

if "from desk_tools import DeskTools" not in text:
    text = text.replace(
        "from tools import BrowserTools",
        "from tools import BrowserTools\nfrom desk_tools import DeskTools\nfrom comet_attach import patch_browser_manager\n",
        1,
    )
if "patch_browser_manager()" not in text:
    if "load_dotenv(" in text:
        import re
        text = re.sub(
            r"(load_dotenv\([^\n]*\)\n)",
            r"\1patch_browser_manager()\n",
            text,
            count=1,
        )
    else:
        text = text.replace(
            "class Assistant",
            "patch_browser_manager()\n\nclass Assistant",
            1,
        )
if "DeskTools" in text and "self.desk_tools" not in text:
    text = text.replace(
        "self.browser_tools = BrowserTools(self.browser)",
        "self.browser_tools = BrowserTools(self.browser)\n        self.desk_tools = DeskTools()",
        1,
    )
if "self.desk_tools.tools" not in text:
    text = text.replace(
        "*self.browser_tools.tools,",
        "*self.desk_tools.tools,\n                *self.browser_tools.tools,",
        1,
    )
agent.write_text(text, encoding="utf-8")
print("agent.py wired")

prompts = SRC / "prompts.py"
ptext = prompts.read_text(encoding="utf-8")
block = (
    "    Your name is Jarvis. Never say you have no name. You are Jarvis, the butler of this house.\n"
    "    You control the user's real Comet browser (already logged in) and the real OS mouse and keyboard.\n"
    "    For desktop apps use look_desktop, focus_window, move_mouse, click_mouse, type_keys, press_hotkey.\n"
    "    For web pages in Comet, use the browser tools after Comet is focused.\n"
)
if "Your name is Jarvis" not in ptext:
    idx = ptext.find("You are Jarvis")
    if idx == -1:
        idx = ptext.find('"""')
        idx = ptext.find("\n", idx) + 1
        ptext = ptext[:idx] + block + ptext[idx:]
    else:
        nl = ptext.find("\n", idx)
        ptext = ptext[: nl + 1] + block + ptext[nl + 1 :]
    prompts.write_text(ptext, encoding="utf-8")
    print("prompts.py named Jarvis + hands")
else:
    print("prompts already named")
print("DONE")
