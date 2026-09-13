# Integrate into jarvis-voice-butler

## 1. Copy

From this repo:

```
src/pel/  → jarvis_new/src/pel/
state/    → jarvis_new/state/
workspace/ → jarvis_new/workspace/
```

## 2. Patch agent.py

Add imports:

```python
from pel.rig import PromptExecutionLayer
```

Inside `Assistant.__init__`, after `BrowserTools`:

```python
self.pel = PromptExecutionLayer(workspace_dir="workspace")
```

In `tools=[...]` add:

```python
*self.pel.tools,
```

## 3. Env

Same as upstream: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `GOOGLE_API_KEY`.

## 4. Optional GitHub session in Playwright

After you sign in once in the visible Chromium window:

```python
await context.storage_state(path="state/github_storage.json")
```

Load that path on next `BrowserManager` start. Do not commit `github_storage.json`.

## 5. Run

```
cd jarvis_new
uv sync
uv run playwright install chromium
uv run src/agent.py dev
```
