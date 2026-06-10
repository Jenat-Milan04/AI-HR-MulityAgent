from typing import Dict, Any
from ..llm import get_llm_provider

class ClarificationAgent:
    """Fallback agent for unclear requests or general assistance."""
    
    def __init__(self):
        self.provider = get_llm_provider()
    
    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process unclear requests and provide clarification."""
        # Add clarification-specific context
        clarification_context = {
            **context,
            "agent_role": "general HR assistant",
            "capabilities": "clarifying requests, general HR guidance, routing to specialists"
        }
        
        return await self.provider.generate(message, clarification_context)