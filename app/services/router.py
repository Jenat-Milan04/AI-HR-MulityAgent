import os
import asyncio
from typing import Dict, Any
from ..agents.scheduler import SchedulingAgent
from ..agents.leave import LeaveAgent  
from ..agents.compliance import ComplianceAgent
from ..agents.clarification import ClarificationAgent

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

class AgentRouter:
    """Route requests to appropriate agents with retry logic."""
    
    def __init__(self):
        self.agents = {
            "SCHEDULING": SchedulingAgent(),
            "LEAVE": LeaveAgent(),
            "COMPLIANCE": ComplianceAgent(),
            "CLARIFICATION": ClarificationAgent()
        }
    
    async def route_request(self, intent: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route request to agent with retry and timeout."""
        agent = self.agents.get(intent, self.agents["CLARIFICATION"])
        
        for attempt in range(MAX_RETRIES):
            try:
                # Execute with timeout
                response = await asyncio.wait_for(
                    agent.process(message, context or {}),
                    timeout=REQUEST_TIMEOUT
                )
                
                return {
                    "response": response,
                    "agent": agent.__class__.__name__,
                    "status": "success",
                    "attempt": attempt + 1
                }
                
            except asyncio.TimeoutError:
                if attempt == MAX_RETRIES - 1:
                    return {
                        "response": "I apologize for the delay. Please try your request again or contact HR directly.",
                        "agent": agent.__class__.__name__,
                        "status": "timeout",
                        "attempt": attempt + 1
                    }
                continue
                
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    return {
                        "response": "I encountered an error processing your request. Please try again or contact HR directly.",
                        "agent": agent.__class__.__name__,
                        "status": "error", 
                        "attempt": attempt + 1
                    }
                continue
        
        # Fallback (shouldn't reach here)
        return {
            "response": "Service temporarily unavailable. Please contact HR directly.",
            "agent": "Unknown",
            "status": "failed",
            "attempt": MAX_RETRIES
        }

router = AgentRouter()