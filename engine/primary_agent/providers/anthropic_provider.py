"""Anthropic provider — Claude Sonnet and Opus."""

import anthropic
from engine.primary_agent.providers.base import BaseProvider
from typing import List

class AnthropicProvider(BaseProvider):
    
    DEFAULT_MODEL = "claude-sonnet-4-6"
    
    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key)
        self.model = model or self.DEFAULT_MODEL
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def send_message(
        self,
        messages: List[dict],
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> str:
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        
        response = await self.client.messages.create(**kwargs)
        return response.content[0].text
    
    async def test_connection(self) -> bool:
        try:
            await self.send_message(
                messages=[{"role": "user", "content": "Reply with OK only."}],
                max_tokens=10
            )
            return True
        except:
            return False
