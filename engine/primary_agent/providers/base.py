"""
Abstract base class for all Primary Agent providers.
Every provider must implement these methods.
"""

from abc import ABC, abstractmethod
from typing import List

class BaseProvider(ABC):
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    async def send_message(
        self,
        messages: List[dict],
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> str:
        """
        Send a conversation to the model and return the response text.
        messages format: [{"role": "user/assistant", "content": "..."}]
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the API key is valid. Returns True if valid."""
        pass
    
    def get_name(self) -> str:
        return self.__class__.__name__.replace("Provider", "")
