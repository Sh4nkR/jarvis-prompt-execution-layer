# Jarvis Prompt Execution Layer (PEL)

English in → use every **enabled** tool already on Jarvis.
This is **not** a fork of the YouTube tutorial repo. It sits **on top** of it.

Upstream agent (cam, browser, DuckDuckGo, Gemini, LiveKit):
https://github.com/ruxakK/jarvis-voice-butler

## What this adds

- `state/capabilities.json` — live map of what is ON
- `set_role` / `remember` / `use_scope` — one spoken/typed goal uses the map
- `run_cmd` — allowlisted commands in `./workspace` only
- No auto-exec of generated tools. Confirm before new code is applied.

## You still do once

1. Clone upstream `jarvis-voice-butler` and copy `src/pel/` from this repo into `jarvis_new/src/pel/`.
2. Add the import lines in `agent.py` shown in `INTEGRATE.md`.
3. Put LiveKit + Gemini keys in `.env.local` (never commit them).
4. Optional: log into GitHub **once** in the headed Playwright window, save storage state (see `INTEGRATE.md`).

After that: *"act like a butler and open my repo README"* is one prompt **if** GitHub session + browser are ON in the map.

## What this will not do

- Train a new model from your PS5.
- Invent PS5 or Android Accessibility if those rows are OFF.
- Store your GitHub password in the prompt (type it in the agent browser).
