# Get running like the YouTube Jarvis (PC)

This repo is the extra Prompt Execution Layer only.
The working voice+cam+browser+Gemini agent is upstream.
There is no prebuilt APK with your Gemini key inside. Keys stay on your machine.

## PC (same shape as the video)

```bat
git clone https://github.com/ruxakK/jarvis-voice-butler.git
cd jarvis-voice-butler
git clone https://github.com/Sh4nkR/jarvis-prompt-execution-layer.git pel-src

xcopy /E /I pel-src\src\pel jarvis_new\src\pel
xcopy /E /I pel-src\state jarvis_new\state
xcopy /E /I pel-src\workspace jarvis_new\workspace
```

On macOS/Linux use `cp -r` instead of `xcopy`.

Then:

```bat
cd jarvis_new
uv sync
uv run playwright install chromium
copy .env.example .env.local
```

Edit `.env.local`:

```
LIVEKIT_URL=wss://YOUR_PROJECT.livekit.cloud
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
GOOGLE_API_KEY=
```

Wire PEL in `src/agent.py` (see INTEGRATE.md), then:

```bat
uv run src/agent.py dev
```

Frontend (second terminal):

```bat
cd jarvis_new\frontend
pnpm install
npm run dev
```

Open http://localhost:3000 — allow mic + camera.

## Phone debug APK

Use upstream Flutter tree:

```bat
cd agent-starter-flutter
flutter pub get
flutter run
```

That is the green Play button path in Android Studio. It talks to the **same LiveKit agent** you started on the PC. It is not a second Gemini and it does not include whisper.cpp or Qwen.

## What I will not put in this Git

- Your API keys
- A finished Play-Store APK
- The entire third-party jarvis-voice-butler source tree copied wholesale
