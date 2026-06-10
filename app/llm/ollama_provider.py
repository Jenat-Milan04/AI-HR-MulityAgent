import os
import httpx
from typing import Dict, Any
from .base import BaseLLMProvider

class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local LLM inference."""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("MODEL_NAME", "llama3")
    
    async def generate(self, message: str, context: Dict[str, Any] = None) -> str:
        """Generate response using Ollama API."""
        try:
            system_prompt = """You are an HR assistant helping employees with leave requests, scheduling, compliance questions, and general HR inquiries. 
Be helpful, professional, and concise. If you need more information, ask clarifying questions."""
            
            prompt = system_prompt + f"\n\nUser: {message}\nAssistant:"
            
            # Add context if available
            if context and context.get("memory"):
                prompt = f"{system_prompt}\n\nContext: {context['memory']}\n\nUser: {message}\nAssistant:"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 200
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    return "I'm having trouble connecting to the local AI service. Please try again or contact HR directly."
                    
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Please try again or contact HR directly. Error: {str(e)}"