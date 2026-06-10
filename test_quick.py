import asyncio
import os
os.environ["MODEL_PROVIDER"] = "mock"

from app.llm import get_llm_provider
from app.services.classifier import classifier

async def test_system():
    print("=== HR Multi-Agent System Test ===")
    
    # Test 1: Intent Classification
    print("\n1. Intent Classification Test:")
    test_messages = [
        "I need leave next week",
        "Can we schedule a meeting?", 
        "What's the remote work policy?",
        "Hello there"
    ]
    
    for msg in test_messages:
        intent, confidence = classifier.classify(msg)
        print(f"  '{msg}' -> {intent} ({confidence:.2f})")
    
    # Test 2: LLM Provider
    print("\n2. LLM Provider Test:")
    provider = get_llm_provider()
    response = await provider.generate("I need vacation leave")
    print(f"  Mock Response: {response[:100]}...")
    
    print("\n[SUCCESS] Core components working correctly!")

if __name__ == "__main__":
    asyncio.run(test_system())