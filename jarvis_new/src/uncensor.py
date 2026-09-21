"""Gemini safety off. LiveKit RealtimeModel does not expose safety_settings."""

from google.genai import types as genai_types

_CATEGORIES = (
    "HARM_CATEGORY_HARASSMENT",
    "HARM_CATEGORY_HATE_SPEECH",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "HARM_CATEGORY_DANGEROUS_CONTENT",
    "HARM_CATEGORY_CIVIC_INTEGRITY",
)


def _threshold():
    return getattr(genai_types.HarmBlockThreshold, "OFF", None) or genai_types.HarmBlockThreshold.BLOCK_NONE


def gemini_safety_settings():
    thresh = _threshold()
    settings = []
    for name in _CATEGORIES:
        cat = getattr(genai_types.HarmCategory, name, None)
        if cat is None:
            continue
        settings.append(genai_types.SafetySetting(category=cat, threshold=thresh))
    return settings


def patch_gemini_live() -> bool:
    """Inject OFF/BLOCK_NONE into Gemini Live connect config."""
    settings = gemini_safety_settings()
    session_cls = None
    for target in (
        "livekit.plugins.google.realtime.realtime_api",
        "livekit.plugins.google.realtime",
        "livekit.plugins.google.beta.realtime.realtime_api",
    ):
        try:
            mod = __import__(target, fromlist=["RealtimeSession"])
            session_cls = getattr(mod, "RealtimeSession", None)
            if session_cls is not None:
                break
        except Exception:
            continue
    if session_cls is None or not hasattr(session_cls, "_build_connect_config"):
        return False
    orig = session_cls._build_connect_config
    if getattr(orig, "_jarvis_uncensored", False):
        return True

    def wrapped(self):
        conf = orig(self)
        conf.safety_settings = settings
        return conf

    wrapped._jarvis_uncensored = True
    session_cls._build_connect_config = wrapped
    return True
