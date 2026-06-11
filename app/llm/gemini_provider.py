import os
import httpx
from typing import Dict, Any
from .base import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider for AI-generated responses."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = "gemini-1.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    async def generate(self, message: str, context: Dict[str, Any] = None) -> str:
        """Generate response using Google Gemini API."""
        # Try different model names - remove 'models/' prefix since base_url already includes it
        models_to_try = [
            "gemini-3.5-flash",
            "gemini-2.5-flash",
            "gemini-2.0-flash", 
            "gemini-flash-latest",
            "gemini-pro-latest"
        ]
        
        for model_name in models_to_try:
            try:
                response = await self._try_gemini_request(message, context, model_name)
                if response and "I'm experiencing technical difficulties" not in response:
                    return response
            except:
                continue
        
        # If all models fail, use smart fallback
        return self._get_smart_hr_response(message, context)
    
    async def _try_gemini_request(self, message: str, context: Dict[str, Any], model: str) -> str:
        """Try Gemini API request with specific model."""
        print(f"[DEBUG] Trying model: {model}")
        
        system_prompt = """You are an HR assistant helping employees with leave requests, scheduling, compliance questions, and general HR inquiries. 
Be helpful, professional, and concise. If you need more information, ask clarifying questions."""
        
        full_prompt = f"{system_prompt}\n\nUser: {message}\nAssistant:"
        
        if context and context.get("memory"):
            full_prompt = f"{system_prompt}\n\nPrevious context: {context['memory']}\n\nUser: {message}\nAssistant:"
        
        request_data = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 800,
                "topP": 1.0,
                "topK": 1
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # All model names include 'models/' prefix now
                url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"
                print(f"[DEBUG] Calling URL: {url}")
                
                response = await client.post(
                    url,
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                
                print(f"[DEBUG] Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"[DEBUG] Response: {result}")
                    
                    if "candidates" in result and len(result["candidates"]) > 0:
                        candidate = result["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            parts = candidate["content"]["parts"]
                            if len(parts) > 0 and "text" in parts[0]:
                                gemini_text = parts[0]['text'].strip()
                                print(f"[DEBUG] Gemini response: {gemini_text}")
                                return f"[GEMINI] {gemini_text}"
                
                print(f"[DEBUG] Failed to extract response from: {response.text}")
                return None
                
        except Exception as e:
            print(f"[DEBUG] Exception: {e}")
            return None
    
    def _get_smart_hr_response(self, message: str, context: Dict[str, Any] = None) -> str:
        """Provide intelligent HR responses when API is unavailable."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["leave", "vacation", "sick", "day off", "holiday"]):
            return "I'd be happy to help you with your leave request. To get started, I'll need to know: What type of leave are you requesting (annual, sick, personal, or emergency)? What are your preferred dates? Have you discussed this with your manager yet? I can also help you check your current leave balance and guide you through our approval process."
        
        elif any(word in message_lower for word in ["schedule", "meeting", "interview", "calendar", "reschedule"]):
            return "I'll assist you with scheduling. Please let me know: What type of meeting or appointment do you need to schedule? Who are the participants? What are your preferred dates and times? I can coordinate with all parties and send out calendar invitations once we confirm the details."
        
        elif any(word in message_lower for word in ["policy", "compliance", "remote", "wfh", "guideline", "rule"]):
            return "I can help you with policy and compliance questions. Our employee handbook covers all current policies including remote work guidelines, time-off procedures, and conduct standards. Which specific policy area would you like information about? I can direct you to the relevant sections and explain any requirements or procedures."
        
        elif any(word in message_lower for word in ["manager", "supervisor", "boss"]):
            return "For matters involving your manager or supervisor, I can help facilitate communication or provide guidance on proper channels. What specific issue or request do you need assistance with regarding your management relationship?"
        
        else:
            return "Welcome! I'm your HR assistant and I'm here to help with all your human resources needs. I can assist you with leave requests, meeting scheduling, policy questions, compliance matters, and general HR inquiries. What can I help you with today?"