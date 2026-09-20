# Attach Jarvis to Comet (this window, your logins)

Playwright used to call `chromium.launch()`. That opens a blank window with no cookies — ChatGPT, Claude, Grok, and DeepSeek look logged out. That path is gone.

Jarvis now **connects to Comet** over Chrome DevTools Protocol and reuses the tab you already have open.

## Once per session

1. Quit Comet completely (every window).
2. Start it with remote debugging, same profile:

```bat
"%LOCALAPPDATA%\Perplexity\Comet\Application\comet.exe" --remote-debugging-port=9222
```

If that path is wrong, open the Start-menu shortcut → Open file location, then add `--remote-debugging-port=9222` to the Target field.

3. In `jarvis_new/.env.local`:

```
JARVIS_CDP_URL=http://127.0.0.1:9222
```

4. Keep the consiglieri in the **favorites bar** (or open them once):
   - https://chatgpt.com/
   - https://claude.ai/new
   - https://grok.com/
   - https://chat.deepseek.com/

5. Run Jarvis as usual. “Take this to Claude” brings that Comet tab forward and types there. No second window. No API keys.

Copy `jarvis_new/src/browser.py`, `tools.py`, `prompts.py` onto `C:\\Users\\twent\\Desktop\\jarvis-voice-butler`.
