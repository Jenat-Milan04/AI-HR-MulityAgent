from typing import Dict, Any
from .base import BaseLLMProvider

class MockLLMProvider(BaseLLMProvider):
    """Mock provider that returns deterministic responses based on keywords."""
    
    async def generate(self, message: str, context: Dict[str, Any] = None) -> str:
        """Generate deterministic response based on message keywords."""
        message_lower = message.lower()
        
        # Leave-related responses
        if any(word in message_lower for word in ["leave", "vacation", "sick", "day off", "holiday"]):
            return "Leave request acknowledged. Please confirm the leave type (annual/sick/personal), dates, and ensure you've notified your manager. I can help you check leave balance if needed."
        
        # Scheduling responses
        if any(word in message_lower for word in ["schedule", "meeting", "interview", "calendar", "reschedule"]):
            return "I can help you with scheduling. Please provide your preferred time slots and I'll check availability. Would you like me to send calendar invites to participants?"
        
        # Compliance responses
        if any(word in message_lower for word in ["policy", "compliance", "remote work", "wfh", "guideline"]):
            return "For compliance and policy questions, please refer to the employee handbook section 4.2. Remote work requires manager approval and adherence to data security protocols."
        
        # Manager-related
        if "manager" in message_lower:
            return "Manager-related requests noted. I can help facilitate communication or escalate to HR if needed."
        
        # Default clarification
        return "I understand you need HR assistance. Could you please provide more details about what specific help you need? I can assist with leave requests, scheduling, policy questions, or other HR matters."