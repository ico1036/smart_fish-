"""LLM client wrapper using Claude CLI (uses Claude Code OAuth automatically)."""
import asyncio
import json
import re
import shutil
import subprocess
from ..config import settings


def _find_claude_cli() -> str:
    """Find the claude CLI binary path."""
    path = shutil.which("claude")
    if path:
        return path
    raise RuntimeError("Claude CLI not found in PATH")


class LLMClient:
    def __init__(self, model: str = None):
        self.model = model or settings.CLAUDE_MODEL
        self._cli_path = _find_claude_cli()

    def _call_cli(self, prompt: str, system_prompt: str = "") -> str:
        """Call claude CLI directly via subprocess."""
        # Remove null bytes that break subprocess args
        prompt = prompt.replace("\x00", "")
        system_prompt = system_prompt.replace("\x00", "")

        cmd = [
            self._cli_path,
            "--output-format", "json",
            "--max-turns", "1",
            "-p", prompt,
        ]
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])

        # Clean environment: remove Claude Code session vars that interfere
        # Clean env: remove vars that interfere with Claude CLI OAuth auth
        import os
        _blocked = {"CLAUDECODE", "ANTHROPIC_API_KEY", "CLAUDE_MODEL", "CLAUDE_SIMULATION_MODEL"}
        clean_env = {k: v for k, v in os.environ.items()
                     if not k.startswith("CLAUDE_CODE") and k not in _blocked}

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            env=clean_env,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude CLI failed (exit {result.returncode})\nstderr: {result.stderr[:500]}\nstdout: {result.stdout[:500]}")

        # Parse JSON output
        try:
            data = json.loads(result.stdout)
            # json output format returns {"type":"result","result":"..."}
            if isinstance(data, dict) and "result" in data:
                text = data["result"]
            elif isinstance(data, dict) and "content" in data:
                text = data["content"]
            else:
                text = result.stdout
        except json.JSONDecodeError:
            text = result.stdout

        text = re.sub(r'<think>[\s\S]*?</think>', '', text).strip()
        return text

    async def _acall_cli(self, prompt: str, system_prompt: str = "") -> str:
        """Async version - runs CLI in thread pool to not block event loop."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._call_cli, prompt, system_prompt)

    def _build_prompt(self, messages: list[dict]) -> tuple[str, str]:
        """Extract system prompt and build user prompt from messages."""
        system = ""
        parts = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                parts.append(msg["content"])
        return "\n\n".join(parts), system

    def chat(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 4096) -> str:
        prompt, system = self._build_prompt(messages)
        return self._call_cli(prompt, system)

    async def achat(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 4096) -> str:
        prompt, system = self._build_prompt(messages)
        return await self._acall_cli(prompt, system)

    def chat_json(self, messages: list[dict], temperature: float = 0.3, max_tokens: int = 4096) -> dict:
        enhanced = self._enhance_for_json(messages)
        response = self.chat(messages=enhanced, temperature=temperature, max_tokens=max_tokens)
        return self._parse_json(response)

    async def achat_json(self, messages: list[dict], temperature: float = 0.3, max_tokens: int = 4096) -> dict:
        enhanced = self._enhance_for_json(messages)
        response = await self.achat(messages=enhanced, temperature=temperature, max_tokens=max_tokens)
        return self._parse_json(response)

    def _enhance_for_json(self, messages: list[dict]) -> list[dict]:
        enhanced = []
        has_system = False
        for msg in messages:
            if msg["role"] == "system":
                enhanced.append({"role": "system", "content": msg["content"] + "\n\nYou MUST respond with ONLY valid JSON. No markdown fences, no explanation, just the JSON object."})
                has_system = True
            else:
                enhanced.append(msg)
        if not has_system:
            enhanced.insert(0, {"role": "system", "content": "Respond with ONLY valid JSON."})
        return enhanced

    def _parse_json(self, response: str) -> dict:
        cleaned = response.strip()
        cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned)
        cleaned = cleaned.strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError(f"LLM returned invalid JSON: {cleaned[:200]}")


def get_llm_client(model: str = None) -> LLMClient:
    return LLMClient(model=model)

def get_fast_llm_client() -> LLMClient:
    return LLMClient(model=settings.CLAUDE_SIM_MODEL)
