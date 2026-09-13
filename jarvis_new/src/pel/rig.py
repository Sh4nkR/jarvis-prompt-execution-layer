from __future__ import annotations

import json
import subprocess
from pathlib import Path

from livekit.agents import RunContext, function_tool

ALLOWED_CMDS = frozenset({"ls", "pwd", "python", "git", "rg", "head", "cat"})


class PromptExecutionLayer:
    def __init__(self, workspace_dir: str = "workspace", state_dir: str = "state") -> None:
        self.workspace = Path(workspace_dir)
        self.state = Path(state_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.state.mkdir(parents=True, exist_ok=True)
        self.cap_path = self.state / "capabilities.json"
        self.role_path = self.state / "role.json"
        self.memory_path = self.state / "memory.md"
        if not self.cap_path.exists():
            self.cap_path.write_text(
                json.dumps(
                    {
                        "cam": True,
                        "browser": True,
                        "duckduckgo": True,
                        "shell_allowlist": True,
                        "memory": True,
                        "github_session": False,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        if not self.role_path.exists():
            self.role_path.write_text('{"role": "jarvis-butler"}', encoding="utf-8")
        if not self.memory_path.exists():
            self.memory_path.write_text("# Memory\n", encoding="utf-8")

    @property
    def tools(self) -> list:
        return [self.use_scope, self.set_role, self.remember, self.read_memory, self.list_capabilities, self.run_cmd]

    def _caps(self) -> dict:
        return json.loads(self.cap_path.read_text(encoding="utf-8") or "{}")

    def _role(self) -> dict:
        return json.loads(self.role_path.read_text(encoding="utf-8") or "{}")

    @function_tool()
    async def list_capabilities(self, context: RunContext) -> dict:
        """Which abilities are ON."""
        return self._caps()

    @function_tool()
    async def set_role(self, context: RunContext, role: str) -> str:
        """Save role from English."""
        data = self._role()
        data["role"] = role.strip()
        self.role_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return f"Role saved: {data['role']}"

    @function_tool()
    async def remember(self, context: RunContext, note: str) -> str:
        """Append memory."""
        with self.memory_path.open("a", encoding="utf-8") as f:
            f.write(f"- {note.strip()}\n")
        return "Saved."

    @function_tool()
    async def read_memory(self, context: RunContext) -> str:
        """Read memory."""
        return self.memory_path.read_text(encoding="utf-8")

    @function_tool()
    async def use_scope(self, context: RunContext, goal: str) -> str:
        """Plan over enabled capabilities only."""
        caps = self._caps()
        on = [k for k, v in caps.items() if v]
        off = [k for k, v in caps.items() if not v]
        return f"Goal: {goal}\nUse: {on}\nDo not claim: {off}\nRole: {self._role().get('role')}"

    @function_tool()
    async def run_cmd(self, context: RunContext, command: str) -> str:
        """Allowlisted command in ./workspace."""
        if not self._caps().get("shell_allowlist", False):
            return "shell off"
        parts = command.strip().split()
        if not parts or parts[0] not in ALLOWED_CMDS:
            return f"blocked: {command!r}"
        try:
            proc = subprocess.run(parts, cwd=self.workspace, capture_output=True, text=True, timeout=20)
        except subprocess.TimeoutExpired:
            return "timeout"
        return ((proc.stdout or "") + (proc.stderr or ""))[-4000:] or f"exit {proc.returncode}"
