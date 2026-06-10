from typing import Dict, Any
from ..llm import get_llm_provider

class ComplianceAgent:
    """Agent for handling compliance, policy, and regulatory questions."""
    
    def __init__(self):
        self.provider = get_llm_provider()
    
    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process compliance-related requests."""
        # Add compliance-specific context
        compliance_context = {
            **context,
            "agent_role": "compliance and policy specialist",
            "capabilities": "policy interpretation, remote work guidelines, compliance requirements"
        }
        
        return await self.provider.generate(message, compliance_context)