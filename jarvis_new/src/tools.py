import json
import os
import urllib.error
import urllib.request
from urllib.parse import urlencode

from livekit.agents import RunContext, function_tool
from livekit.agents.llm import ToolError

from browser import BrowserError, BrowserManager


def _deepseek_api(question: str) -> str:
    key = (os.getenv("DEEPSEEK_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("no_api_key")
    model = os.getenv("DEEPSEEK_MODEL") or "deepseek-chat"
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "Be concise. Give reference, guidance, or code when asked.",
                },
                {"role": "user", "content": question},
            ],
            "temperature": 0.3,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"DeepSeek API HTTP {exc.code}") from exc
    return data["choices"][0]["message"]["content"]


class BrowserTools:
    def __init__(self, browser: BrowserManager) -> None:
        self.browser = browser

    @property
    def tools(self) -> list:
        return [self.open_url, self.search_the_web, self.read_page, self.ask_deepseek]

    @function_tool()
    async def open_url(self, context: RunContext, url: str) -> dict:
        """Open an http(s) URL in the agent browser."""
        try:
            return await self.browser.open_url(url)
        except BrowserError as exc:
            raise ToolError(str(exc)) from exc

    @function_tool()
    async def search_the_web(self, context: RunContext, query: str) -> dict:
        """DuckDuckGo search when no specific site was named."""
        q = query.strip()
        if not q:
            raise ToolError("Empty query")
        url = f"https://duckduckgo.com/?{urlencode({'q': q})}"
        try:
            return await self.browser.open_url(url)
        except BrowserError as exc:
            raise ToolError(str(exc)) from exc

    @function_tool()
    async def read_page(self, context: RunContext) -> dict:
        """Read visible text of the current page."""
        try:
            return await self.browser.read_page()
        except BrowserError as exc:
            raise ToolError(str(exc)) from exc

    @function_tool()
    async def ask_deepseek(self, context: RunContext, question: str) -> dict:
        """Ask DeepSeek for reference, guidance, or code.
        Uses DEEPSEEK_API_KEY when set. Otherwise opens chat.deepseek.com in the agent browser.
        """
        q = question.strip()
        if not q:
            raise ToolError("Empty question")
        try:
            text = _deepseek_api(q)
            return {"source": "deepseek_api", "text": text}
        except RuntimeError as exc:
            if str(exc) != "no_api_key" and "HTTP" not in str(exc):
                raise ToolError(str(exc)) from exc
        try:
            result = await self.browser.ask_deepseek(q)
            result["source"] = "deepseek_web"
            return result
        except BrowserError as exc:
            raise ToolError(str(exc)) from exc
