from __future__ import annotations

import asyncio
from urllib.parse import urlparse

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


class BrowserError(Exception):
    pass


class BrowserManager:
    def __init__(self, *, headless: bool = False, timeout_ms: int = 15000) -> None:
        self._headless = headless
        self._timeout_ms = timeout_ms
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        if self._page is not None:
            return
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self._headless)
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()
        self._page.set_default_timeout(self._timeout_ms)

    async def close(self) -> None:
        async with self._lock:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            self._page = self._context = self._browser = self._playwright = None

    async def _page_ready(self):
        if self._page is None:
            await self.start()
        return self._page

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
            return {"url": page.url, "title": await page.title(), "text": text[:8000]}
