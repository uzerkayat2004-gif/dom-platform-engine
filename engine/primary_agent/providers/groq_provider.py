"""Groq provider — Llama 3.3 70B Versatile. Fast, free tier available."""

from groq import AsyncGroq
from engine.primary_agent.providers.base import BaseProvider
from typing import List

class GroqProvider(BaseProvider):
    
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    
    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key)
        self.model = model or self.DEFAULT_MODEL
        self.client = AsyncGroq(api_key=api_key)
    
    async def send_message(
        self,
        messages: List[dict],
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> str:
        formatted = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        formatted.extend(messages)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=formatted,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    async def test_connection(self) -> bool:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Reply with OK only."}],
                max_tokens=10
            )
            return True
        except:
            return False
