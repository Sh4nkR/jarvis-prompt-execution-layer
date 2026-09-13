# LiveKit voice clone

LiveKit does not clone inside Gemini realtime. Clone = TTS voice ID.
This repo uses **your** ElevenLabs instant clone, then LiveKit speaks with it.

## 1. Consent
Only clone audio of a voice you own or have rights to use.

## 2. Sample
Put a short clean clip at `workspace/my_voice.wav`.

## 3. Create clone
```
cd jarvis_new
uv sync
uv run src/voice_clone.py workspace/my_voice.wav jarvis-clone
```
Copy printed `voice_id` into `.env.local`:
```
ELEVEN_API_KEY=...
ELEVENLABS_VOICE_ID=...
USE_CLONED_VOICE=true
```

## 4. Run agent
```
uv run src/agent.py dev
```

Pipeline becomes: LiveKit STT → Gemini text LLM → ElevenLabs TTS (cloned voice).
Default (`USE_CLONED_VOICE=false`) stays Gemini realtime Enceladus.

## LiveKit Cloud custom voices
Paid LiveKit plans can clone in the Cloud dashboard to a `v_*` id and use `inference.TTS`. Not wired here.
