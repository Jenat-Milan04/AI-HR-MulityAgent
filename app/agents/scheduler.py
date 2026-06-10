from typing import Dict, Any
from ..llm import get_llm_provider

class SchedulingAgent:
    """Agent for handling scheduling, meetings, and calendar requests."""
    
    def __init__(self):
        self.provider = get_llm_provider()
    
    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process scheduling-related requests."""
        # Add scheduling-specific context
        scheduling_context = {
            **context,
            "agent_role": "scheduling specialist",
            "capabilities": "meeting scheduling, calendar management, interview coordination"
        }
        
        return await self.provider.generate(message, scheduling_context)