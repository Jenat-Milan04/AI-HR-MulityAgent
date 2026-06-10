from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from ..memory import stm, ltm
from .classifier import classifier
from .router import router
from .audit import audit_logger

class OrchestrationState(TypedDict):
    user_id: str
    message: str
    memory_context: str
    intent: str
    confidence: float
    response: str
    agent: str
    status: str

class HROrchestrator:
    """LangGraph-based orchestration workflow."""
    
    def __init__(self):
        # Create state graph
        workflow = StateGraph(OrchestrationState)
        
        # Add nodes
        workflow.add_node("memory_lookup", self.memory_lookup)
        workflow.add_node("classify_intent", self.classify_intent)  
        workflow.add_node("route_agent", self.route_agent)
        workflow.add_node("save_memory", self.save_memory)
        workflow.add_node("save_audit", self.save_audit)
        
        # Add edges
        workflow.set_entry_point("memory_lookup")
        workflow.add_edge("memory_lookup", "classify_intent")
        workflow.add_edge("classify_intent", "route_agent")
        workflow.add_edge("route_agent", "save_memory")
        workflow.add_edge("save_memory", "save_audit")
        workflow.add_edge("save_audit", END)
        
        self.app = workflow.compile()
    
    async def memory_lookup(self, state: OrchestrationState) -> OrchestrationState:
        """Fetch STM + LTM context."""
        stm_entries = await stm.get_entries(state["user_id"])
        ltm_entries = await ltm.get_entries(state["user_id"], limit=10)
        
        # Combine memory context
        context_parts = []
        if stm_entries:
            recent = [entry["message"] for entry in stm_entries[:3]]
            context_parts.append(f"Recent: {'; '.join(recent)}")
        if ltm_entries:
            significant = [entry["message"] for entry in ltm_entries[:3]]
            context_parts.append(f"Important: {'; '.join(significant)}")
        
        state["memory_context"] = " | ".join(context_parts) if context_parts else ""
        return state
    
    async def classify_intent(self, state: OrchestrationState) -> OrchestrationState:
        """Classify user intent."""
        intent, confidence = classifier.classify(state["message"])
        state["intent"] = intent
        state["confidence"] = confidence
        return state
    
    async def route_agent(self, state: OrchestrationState) -> OrchestrationState:
        """Route to appropriate agent."""
        context = {"memory": state["memory_context"]} if state["memory_context"] else {}
        
        result = await router.route_request(state["intent"], state["message"], context)
        
        state["response"] = result["response"]
        state["agent"] = result["agent"] 
        state["status"] = result["status"]
        return state
    
    async def save_memory(self, state: OrchestrationState) -> OrchestrationState:
        """Save to STM and conditionally to LTM."""
        # Always save to STM
        await stm.add_entry(state["user_id"], state["message"])
        
        # Save to LTM if significant
        await ltm.add_entry_if_significant(state["user_id"], state["message"])
        
        return state
    
    async def save_audit(self, state: OrchestrationState) -> OrchestrationState:
        """Log to audit trail."""
        await audit_logger.log_request(
            user_id=state["user_id"],
            request=state["message"],
            intent=state["intent"],
            agent=state["agent"],
            response=state["response"],
            status=state["status"]
        )
        return state
    
    async def process_request(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process a user request through the complete workflow."""
        initial_state = OrchestrationState(
            user_id=user_id,
            message=message,
            memory_context="",
            intent="",
            confidence=0.0,
            response="",
            agent="",
            status=""
        )
        
        final_state = await self.app.ainvoke(initial_state)
        
        return {
            "user_id": final_state["user_id"],
            "response": final_state["response"],
            "intent": final_state["intent"],
            "confidence": final_state["confidence"],
            "agent": final_state["agent"],
            "status": final_state["status"]
        }

orchestrator = HROrchestrator()