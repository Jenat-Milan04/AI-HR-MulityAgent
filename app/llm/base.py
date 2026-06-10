from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLLMProvider(ABC):
    """Base class for all LLM providers."""
    
    @abstractmethod
    async def generate(self, message: str, context: Dict[str, Any] = None) -> str:
        """Generate a response to the message with optional context."""
        pass