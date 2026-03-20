"""Nvidia provider — uses OpenAI-compatible API with Nvidia base URL."""

from engine.primary_agent.providers.openai_provider import OpenAIProvider

class NvidiaProvider(OpenAIProvider):
    DEFAULT_MODEL = "meta/llama-3.3-70b-instruct"
    BASE_URL = "https://integrate.api.nvidia.com/v1"
    
    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model or self.DEFAULT_MODEL, self.BASE_URL)
