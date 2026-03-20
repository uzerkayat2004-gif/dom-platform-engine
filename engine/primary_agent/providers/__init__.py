"""
Pluggable provider system for the Primary Agent.
Every provider inherits from BaseProvider.
Add any new AI provider by implementing BaseProvider.
"""

from engine.primary_agent.providers.base import BaseProvider

def get_provider(provider_name: str, api_key: str) -> BaseProvider:
    """Factory function — returns the correct provider instance."""
    providers = {
        "groq": "engine.primary_agent.providers.groq_provider.GroqProvider",
        "anthropic": "engine.primary_agent.providers.anthropic_provider.AnthropicProvider",
        "openai": "engine.primary_agent.providers.openai_provider.OpenAIProvider",
        "nvidia": "engine.primary_agent.providers.nvidia.NvidiaProvider",
        "openrouter": "engine.primary_agent.providers.openrouter.OpenRouterProvider",
    }
    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}")
    module_path, class_name = providers[provider_name].rsplit(".", 1)
    import importlib
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(api_key=api_key)
