import os

from dotenv import load_dotenv
from google.genai import types as genai_types
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    TurnHandlingOptions,
    cli,
    inference,
    room_io,
)
from livekit.plugins import elevenlabs, google

from browser import BrowserManager
from pel.rig import PromptExecutionLayer
from prompts import AGENT_INSTRUCTIONS
from tools import BrowserTools

load_dotenv(".env.local")

USE_CLONED_VOICE = os.getenv("USE_CLONED_VOICE", "false").lower() in {"1", "true", "yes"}
ELEVEN_VOICE = (os.getenv("ELEVENLABS_VOICE_ID") or "").strip()
ELEVEN_MODEL = os.getenv("ELEVENLABS_MODEL_ID") or "eleven_multilingual_v2"


class Assistant(Agent):
    def __init__(self, browser: BrowserManager | None = None) -> None:
        self.browser = browser or BrowserManager(headless=False)
        self.browser_tools = BrowserTools(self.browser)
        self.pel = PromptExecutionLayer(workspace_dir="workspace", state_dir="state")
        tools = [*self.browser_tools.tools, *self.pel.tools]
        if USE_CLONED_VOICE:
            super().__init__(
                llm=google.LLM(model="gemini-2.5-flash"),
                instructions=AGENT_INSTRUCTIONS,
                tools=tools,
            )
        else:
            super().__init__(
                llm=google.beta.realtime.RealtimeModel(
                    model="gemini-2.5-flash-preview-native-audio-dialog",
                    voice="Enceladus",
                    language="en-GB",
                    tool_response_scheduling=genai_types.FunctionResponseScheduling.INTERRUPT,
                ),
                instructions=AGENT_INSTRUCTIONS,
                tools=tools,
            )


server = AgentServer()


@server.rtc_session(agent_name="jarvis-pel")
async def jarvis(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    browser = BrowserManager(headless=False)
    ctx.add_shutdown_callback(browser.close)

    if USE_CLONED_VOICE:
        if not ELEVEN_VOICE:
            raise RuntimeError("USE_CLONED_VOICE=true needs ELEVENLABS_VOICE_ID")
        session = AgentSession(
            stt=inference.STT(),
            tts=elevenlabs.TTS(voice_id=ELEVEN_VOICE, model=ELEVEN_MODEL),
            turn_handling=TurnHandlingOptions(
                turn_detection=inference.TurnDetector(),
                interruption={"mode": "adaptive"},
                preemptive_generation={"enabled": True},
            ),
        )
    else:
        session = AgentSession(
            turn_handling=TurnHandlingOptions(
                turn_detection=inference.TurnDetector(),
                interruption={"mode": "adaptive"},
                preemptive_generation={"enabled": True},
            )
        )

    await session.start(
        agent=Assistant(browser),
        room=ctx.room,
        room_options=room_io.RoomOptions(video_input=True),
    )
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
