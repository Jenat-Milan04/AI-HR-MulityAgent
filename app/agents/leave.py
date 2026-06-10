from typing import Dict, Any
from ..llm import get_llm_provider

class LeaveAgent:
    """Agent for handling leave requests and time-off management."""
    
    def __init__(self):
        self.provider = get_llm_provider()
    
    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process leave-related requests."""
        # Add leave-specific context
        leave_context = {
            **context,
            "agent_role": "leave management specialist", 
            "capabilities": "leave requests, vacation planning, sick leave, leave balance inquiries"
        }
        
        return await self.provider.generate(message, leave_context)