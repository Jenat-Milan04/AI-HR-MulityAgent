import os
import httpx
from typing import Dict, Any
from .base import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    """Google Gemini via OpenRouter API provider."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("MODEL_NAME", "google/gemini-2.0-flash-exp:free")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    async def generate(self, message: str, context: Dict[str, Any] = None) -> str:
        """Generate response using OpenRouter Gemini API."""
        try:
            response = await self._try_openrouter_request(message, context)
            if response:
                return response
        except Exception as e:
            print(f"[DEBUG] Exception: {e}")
        
        return self._get_smart_hr_response(message, context)
    
    async def _try_openrouter_request(self, message: str, context: Dict[str, Any] = None) -> str:
        """Try OpenRouter API request."""
        print(f"[DEBUG] Trying model: {self.model}")
        
        system_prompt = """You are an HR assistant helping employees with leave requests, scheduling, compliance questions, and general HR inquiries. 
Be helpful, professional, and concise. If you need more information, ask clarifying questions."""

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        if context and context.get("memory"):
            messages.append({"role": "system", "content": f"Previous context: {context['memory']}"})

        messages.append({"role": "user", "content": message})

        request_data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 800
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://hr-agent.local",
            "X-Title": "HR Agent"
        }

        print(f"[DEBUG] Calling OpenRouter with model: {self.model}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                json=request_data,
                headers=headers,
                timeout=30.0
            )

            print(f"[DEBUG] Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"[DEBUG] Full response: {result}")
                if "choices" in result and len(result["choices"]) > 0:
                    text = result["choices"][0]["message"]["content"].strip()
                    print(f"[DEBUG] Gemini response: {text}")
                    return f"[GEMINI] {text}"
            else:
                print(f"[DEBUG] Error response: {response.text}")

        return None
    
    def _get_smart_hr_response(self, message: str, context: Dict[str, Any] = None) -> str:
        """Fallback HR responses when API is unavailable."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["leave", "vacation", "sick", "day off", "holiday"]):
            return "I'd be happy to help with your leave request. What type of leave and what dates do you need?"
        
        elif any(word in message_lower for word in ["schedule", "meeting", "interview", "calendar"]):
            return "I'll assist with scheduling. What type of meeting and what dates work for you?"
        
        elif any(word in message_lower for word in ["policy", "compliance", "remote", "wfh", "guideline"]):
            return "I can help with policy questions. Which specific policy area do you need information about?"
        
        else:
            return "Welcome! I'm your HR assistant. I can help with leave requests, scheduling, policy questions, and HR inquiries. What can I help you with today?"