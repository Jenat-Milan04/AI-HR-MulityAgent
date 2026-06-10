import os
import pytest
import asyncio
from fastapi.testclient import TestClient

# Set test environment
os.environ["DB_PATH"] = ":memory:"
os.environ["MODEL_PROVIDER"] = "mock"

from app.main import app
from app.db.database import init_database
from app.memory import stm, ltm
from app.services import classifier, orchestrator

client = TestClient(app)

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Initialize test database before each test."""
    await init_database()

class TestIntentClassification:
    """Test intent classification functionality."""
    
    def test_leave_classification(self):
        intent, confidence = classifier.classify("I need leave next Friday")
        assert intent == "LEAVE"
        assert confidence >= 0.5
    
    def test_scheduling_classification(self):
        intent, confidence = classifier.classify("Can we schedule a meeting tomorrow?")
        assert intent == "SCHEDULING"
        assert confidence >= 0.5
    
    def test_compliance_classification(self):
        intent, confidence = classifier.classify("What's the remote work policy?")
        assert intent == "COMPLIANCE"
        assert confidence >= 0.5
    
    def test_clarification_fallback(self):
        intent, confidence = classifier.classify("Hello")
        assert intent == "CLARIFICATION"

class TestMemorySystem:
    """Test STM and LTM functionality."""
    
    async def test_stm_ring_buffer(self):
        user_id = "test_user_stm"
        
        # Add more entries than STM limit
        for i in range(15):
            await stm.add_entry(user_id, f"Message {i}")
        
        entries = await stm.get_entries(user_id)
        assert len(entries) <= 10  # STM_MAX_ENTRIES
    
    async def test_ltm_significance_gating(self):
        user_id = "test_user_ltm"
        
        # Low significance message
        added = await ltm.add_entry_if_significant(user_id, "hello")
        assert not added
        
        # High significance message
        added = await ltm.add_entry_if_significant(
            user_id, 
            "I need annual leave and my manager Sarah needs to approve policy compliance"
        )
        assert added
        
        entries = await ltm.get_entries(user_id)
        assert len(entries) == 1

class TestAPIEndpoints:
    """Test all API endpoints."""
    
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_hr_request_endpoint(self):
        response = client.post("/request", json={
            "user_id": "test_user",
            "message": "I need leave next week"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert data["intent"] == "LEAVE"
        assert data["status"] == "success"
    
    def test_audit_endpoint(self):
        # First make a request to generate audit log
        client.post("/request", json={
            "user_id": "audit_test",
            "message": "Schedule meeting"
        })
        
        # Then check audit logs
        response = client.get("/audit?user_id=audit_test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_memory_endpoint(self):
        user_id = "memory_test"
        
        # Make request to populate memory
        client.post("/request", json={
            "user_id": user_id,
            "message": "I need vacation leave"
        })
        
        # Check memory
        response = client.get(f"/memory/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert len(data["stm_entries"]) >= 1

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_request_format(self):
        response = client.post("/request", json={
            "user_id": "test",
            "message": ""  # Empty message should fail validation
        })
        assert response.status_code == 422
    
    def test_missing_user_memory(self):
        response = client.get("/memory/nonexistent_user")
        assert response.status_code == 200  # Should return empty memory
        data = response.json()
        assert len(data["stm_entries"]) == 0
        assert len(data["ltm_entries"]) == 0

class TestOrchestrationWorkflow:
    """Test the complete orchestration workflow."""
    
    async def test_complete_workflow(self):
        result = await orchestrator.process_request(
            user_id="workflow_test",
            message="I need to schedule leave for next month"
        )
        
        assert result["user_id"] == "workflow_test"
        assert result["response"] is not None
        assert result["intent"] in ["LEAVE", "SCHEDULING", "CLARIFICATION"]
        assert result["status"] == "success"
        assert result["agent"] is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])