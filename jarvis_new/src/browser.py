from __future__ import annotations

import asyncio
import os
from urllib.parse import urlencode, urlparse

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright


class BrowserError(Exception):
    pass


CONSUL = {
    "chatgpt": {
        "host": "chatgpt.com",
        "home": "https://chatgpt.com/",
        "query": lambda q: f"https://chatgpt.com/?{urlencode({'q': q})}",
    },
    "claude": {
        "host": "claude.ai",
        "home": "https://claude.ai/new",
        "query": lambda q: f"https://claude.ai/new?{urlencode({'q': q})}",
    },
    "grok": {
        "host": "grok.com",
        "home": "https://grok.com/",
        "query": lambda q: f"https://grok.com/?{urlencode({'q': q})}",
    },
    "deepseek": {
        "host": "deepseek.com",
        "home": "https://chat.deepseek.com/",
        "query": None,
    },
}


class BrowserManager:
    """Ride the boss's Comet (CDP). Never launch a second Chromium."""

    def __init__(self, *, headless: bool = False, timeout_ms: int = 15000) -> None:
        self._headless = headless
        self._timeout_ms = timeout_ms
        self._cdp = (os.getenv("JARVIS_CDP_URL") or "http://127.0.0.1:9222").strip()
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        if self._page is not None:
            return
        self._playwright = await async_playwright().start()
        try:
            self._browser = await self._playwright.chromium.connect_over_cdp(self._cdp)
        except Exception as exc:
            raise BrowserError(
                "Comet is not on the line. Close Comet, relaunch it with "
                "--remote-debugging-port=9222, then retry. I will not open a "
                "second browser."
            ) from exc
        if self._browser.contexts:
            self._context = self._browser.contexts[0]
        else:
            self._context = await self._browser.new_context()
        pages = self._context.pages
        self._page = pages[0] if pages else await self._context.new_page()
        self._page.set_default_timeout(self._timeout_ms)

    async def close(self) -> None:
        async with self._lock:
            if self._playwright:
                await self._playwright.stop()
            self._page = self._context = self._browser = self._playwright = None

    async def _page_ready(self):
        if self._page is None:
            await self.start()
        return self._page

    def _all_pages(self):
        pages = []
        if self._browser is None:
            return pages
        for ctx in self._browser.contexts:
            pages.extend(ctx.pages)
        return pages

    async def _tab_for(self, host: str):
        await self._page_ready()
        for page in self._all_pages():
            if host in (page.url or ""):
                await page.bring_to_front()
                self._page = page
                return page
        page = self._page
        await page.bring_to_front()
        return page

    @staticmethod
    def _check_url(url: str) -> None:
        p = urlparse(url.strip())
        if p.scheme not in {"http", "https"} or not p.netloc:
            raise BrowserError("Need a full http or https URL.")

    async def open_url(self, url: str) -> dict:
        self._check_url(url)
        page = await self._page_ready()
        async with self._lock:
            try:
                await page.goto(url, wait_until="domcontentloaded")
                return {"url": page.url, "title": await page.title()}
            except PlaywrightTimeoutError as exc:
                raise BrowserError("Page load timed out.") from exc

    async def read_page(self) -> dict:
        page = await self._page_ready()
        async with self._lock:
            text = await page.locator("body").inner_text()
            return {"url": page.url, "title": await page.title(), "text": text[:12000]}

    async def ask_consigliere(self, seat: str, prompt: str) -> dict:
        key = seat.strip().lower()
        aliases = {
            "gpt": "chatgpt",
            "chat": "chatgpt",
            "diplomat": "chatgpt",
            "counsel": "claude",
            "anthropic": "claude",
            "xai": "grok",
            "straight": "grok",
            "quiet": "deepseek",
            "ds": "deepseek",
        }
        key = aliases.get(key, key)
        spec = CONSUL.get(key)
        if spec is None:
            raise BrowserError("Unknown seat. Use chatgpt, claude, grok, or deepseek.")
        q = prompt.strip()[:4000]
        if not q:
            raise BrowserError("Empty order.")

        async with self._lock:
            page = await self._tab_for(spec["host"])
            try:
                if spec["query"]:
                    await page.goto(spec["query"](q), wait_until="domcontentloaded")
                else:
                    if spec["host"] not in (page.url or ""):
                        await page.goto(spec["home"], wait_until="domcontentloaded")
                    box = page.locator("textarea").last
                    await box.click()
                    await box.fill(q)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(4000)
                await page.bring_to_front()
                return {
                    "seat": key,
                    "url": page.url,
                    "title": await page.title(),
                    "mode": "same_tab",
                }
            except PlaywrightTimeoutError as exc:
                raise BrowserError(f"{key} took too long.") from exc
            except Exception as exc:
                raise BrowserError(f"Could not sit {key} in this Comet tab ({exc}).") from exc

    async def ask_deepseek(self, prompt: str) -> dict:
        return await self.ask_consigliere("deepseek", prompt)
