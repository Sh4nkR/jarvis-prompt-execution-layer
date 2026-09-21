from __future__ import annotations

CDP = "http://127.0.0.1:9222"


def patch_browser_manager() -> None:
    from browser import BrowserManager

    orig_start = BrowserManager.start
    orig_close = BrowserManager.close

    async def start(self):
        if getattr(self, "_page", None) is not None:
            return
        try:
            from playwright.async_api import async_playwright

            pw = await async_playwright().start()
            browser = await pw.chromium.connect_over_cdp(CDP)
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = context.pages[-1] if context.pages else await context.new_page()
            self._playwright = pw
            self._browser = browser
            self._context = context
            self._page = page
            self._cdp = True
            if hasattr(page, "set_default_timeout"):
                page.set_default_timeout(getattr(self, "_timeout_ms", 15000))
            return
        except Exception:
            self._cdp = False
            await orig_start(self)

    async def close(self):
        if getattr(self, "_cdp", False):
            pw = getattr(self, "_playwright", None)
            if pw is not None:
                await pw.stop()
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None
            self._cdp = False
            return
        await orig_close(self)

    BrowserManager.start = start
    BrowserManager.close = close
