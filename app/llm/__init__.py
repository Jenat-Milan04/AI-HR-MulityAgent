import os
from .base import BaseLLMProvider
from .mock_provider import MockLLMProvider
from .gemini_provider import GeminiProvider

def get_llm_provider() -> BaseLLMProvider:
    """Factory function to get the configured LLM provider."""
    provider_type = os.getenv("MODEL_PROVIDER", "gemini").lower()
    print(f"[DEBUG] MODEL_PROVIDER = {provider_type}")
    
    if provider_type == "gemini":
        print("[DEBUG] Using GeminiProvider")
        return GeminiProvider()
    else:
        print("[DEBUG] Using MockLLMProvider")
        return MockLLMProvider()