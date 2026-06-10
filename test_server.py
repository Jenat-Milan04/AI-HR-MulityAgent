import asyncio
import os
import signal
import sys
from contextlib import asynccontextmanager

# Set environment
os.environ["MODEL_PROVIDER"] = "mock"
os.environ["DB_PATH"] = ":memory:"

async def test_server():
    """Test server initialization without actually starting it."""
    try:
        # Import and initialize app components
        from app.main import app
        from app.db.database import init_database
        
        # Initialize database
        await init_database()
        print("[OK] Database initialized")
        
        # Test app creation
        assert app is not None
        print("[OK] FastAPI app created")
        
        # Test route registration
        routes = [route.path for route in app.routes]
        expected_routes = ["/request", "/audit", "/memory/{user_id}", "/memory", "/health"]
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"[OK] Route {route} registered")
            else:
                print(f"[MISSING] Route {route} missing")
        
        print("\n[SUCCESS] Server components ready!")
        return True
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)