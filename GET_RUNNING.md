# Run (LiveKit is in this repo)

```bat
git clone https://github.com/Sh4nkR/jarvis-prompt-execution-layer.git
cd jarvis-prompt-execution-layer\jarvis_new
uv sync
uv run playwright install chromium
copy .env.example .env.local
```

Fill `.env.local` with LiveKit Cloud URL/key/secret and `GOOGLE_API_KEY`.

```bat
uv run src/agent.py dev
```

Then open the playground link printed in the terminal. Allow mic and camera.

LiveKit is required: it is the room that carries voice + camera frames to Gemini and carries tool calls to Playwright/PEL.
