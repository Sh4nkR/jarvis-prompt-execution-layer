from __future__ import annotations

import asyncio
import ctypes
from ctypes import wintypes

from livekit.agents import RunContext, function_tool
from livekit.agents.llm import ToolError

import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def _window_titles() -> list[str]:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    titles: list[str] = []
    enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    @enum_proc
    def collect(hwnd: int, _: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value.strip()
        if title:
            titles.append(title)
        return True

    user32.EnumWindows(collect, 0)
    return titles[:40]


def _focus(title: str) -> bool:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    found: list[int] = []

    @enum_proc
    def collect(hwnd: int, _: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        if title.casefold() in buf.value.casefold():
            found.append(hwnd)
            return False
        return True

    user32.EnumWindows(collect, 0)
    if not found:
        return False
    hwnd = found[0]
    user32.ShowWindow(hwnd, 9)
    return bool(user32.SetForegroundWindow(hwnd))


class DeskTools:
    @property
    def tools(self) -> list:
        return [
            self.look_desktop,
            self.focus_window,
            self.move_mouse,
            self.click_mouse,
            self.scroll_mouse,
            self.type_keys,
            self.press_hotkey,
        ]

    @function_tool()
    async def look_desktop(self, context: RunContext) -> dict:
        """See screen size, mouse position, and open window titles. Call this before clicking."""
        w, h = pyautogui.size()
        x, y = pyautogui.position()
        titles = await asyncio.to_thread(_window_titles)
        return {"screen": [w, h], "mouse": [x, y], "windows": titles}

    @function_tool()
    async def focus_window(self, context: RunContext, title: str) -> str:
        """Bring a window to the front by part of its title, e.g. Comet, YouTube, Notepad."""
        ok = await asyncio.to_thread(_focus, title)
        if not ok:
            raise ToolError(f"No window matching {title!r}. Call look_desktop first.")
        return f"Focused window matching {title!r}."

    @function_tool()
    async def move_mouse(self, context: RunContext, x: int, y: int) -> str:
        """Move the OS mouse to screen pixel x,y. Origin is top-left."""
        w, h = pyautogui.size()
        x = max(0, min(int(x), w - 2))
        y = max(0, min(int(y), h - 2))
        await asyncio.to_thread(pyautogui.moveTo, x, y, 0.15)
        return f"Mouse at {x},{y}."

    @function_tool()
    async def click_mouse(
        self,
        context: RunContext,
        x: int | None = None,
        y: int | None = None,
        button: str = "left",
        clicks: int = 1,
    ) -> str:
        """Click the OS mouse. Pass x,y to move then click, or omit to click current position."""
        if button not in {"left", "right", "middle"}:
            raise ToolError("button must be left, right, or middle")
        clicks = 1 if clicks not in (1, 2) else clicks

        def _do() -> str:
            if x is not None and y is not None:
                pyautogui.click(int(x), int(y), clicks=clicks, button=button)
                return f"Clicked {button} at {int(x)},{int(y)}."
            pyautogui.click(clicks=clicks, button=button)
            return f"Clicked {button} at current position."

        return await asyncio.to_thread(_do)

    @function_tool()
    async def scroll_mouse(self, context: RunContext, amount: int) -> str:
        """Scroll the OS mouse wheel. Positive amount scrolls up, negative scrolls down."""
        await asyncio.to_thread(pyautogui.scroll, int(amount))
        return f"Scrolled {amount}."

    @function_tool()
    async def type_keys(self, context: RunContext, text: str) -> str:
        """Type into the focused window as a human keyboard. Use for desktop apps and Comet."""
        if not text:
            raise ToolError("text is empty")
        await asyncio.to_thread(pyautogui.write, text, 0.02)
        return f"Typed {len(text)} characters."

    @function_tool()
    async def press_hotkey(self, context: RunContext, keys: str) -> str:
        """Press a hotkey combo. Example: ctrl+l, ctrl+t, alt+tab, enter, esc, win+e."""
        parts = [p.strip().lower() for p in keys.replace("-", "+").split("+") if p.strip()]
        if not parts:
            raise ToolError("keys is empty")
        await asyncio.to_thread(lambda: pyautogui.hotkey(*parts))
        return f"Pressed {'+'.join(parts)}."
