"""LLM client wrapper for Anthropic Claude API."""
import json
import re
from anthropic import Anthropic
from ..config import settings


class LLMClient:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.CLAUDE_MODEL
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        self.client = Anthropic(api_key=self.api_key)

    def chat(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 4096) -> str:
        system = None
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                user_messages.append(msg)

        kwargs = {"model": self.model, "messages": user_messages, "temperature": temperature, "max_tokens": max_tokens}
        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        content = response.content[0].text
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content

    def chat_json(self, messages: list[dict], temperature: float = 0.3, max_tokens: int = 4096) -> dict:
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

        response = self.chat(messages=enhanced, temperature=temperature, max_tokens=max_tokens)
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
