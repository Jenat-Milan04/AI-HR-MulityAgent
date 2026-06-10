import os
from .base import BaseLLMProvider
from .mock_provider import MockLLMProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider

def get_llm_provider() -> BaseLLMProvider:
    """Factory function to get the configured LLM provider."""
    provider_type = os.getenv("MODEL_PROVIDER", "mock").lower()
    
    if provider_type == "openai":
        return OpenAIProvider()
    elif provider_type == "ollama":
        return OllamaProvider()
    else:
        return MockLLMProvider()