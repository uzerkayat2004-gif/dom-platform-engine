"""OpenAI provider — GPT-4o and GPT-4o-mini."""

from openai import AsyncOpenAI
from engine.primary_agent.providers.base import BaseProvider
from typing import List

class OpenAIProvider(BaseProvider):
    
    DEFAULT_MODEL = "gpt-4o"
    
    def __init__(self, api_key: str, model: str = None, base_url: str = None):
        super().__init__(api_key)
        self.model = model or self.DEFAULT_MODEL
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
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
            await self.send_message(
                messages=[{"role": "user", "content": "Reply with OK only."}],
                max_tokens=10
            )
            return True
        except:
            return False
