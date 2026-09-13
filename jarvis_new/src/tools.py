from urllib.parse import urlencode

from livekit.agents import RunContext, function_tool
from livekit.agents.llm import ToolError

from browser import BrowserError, BrowserManager


class BrowserTools:
    def __init__(self, browser: BrowserManager) -> None:
        self.browser = browser

    @property
    def tools(self) -> list:
        return [self.open_url, self.search_the_web, self.read_page]

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
