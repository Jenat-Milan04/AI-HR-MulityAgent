import os
from typing import Dict, Any
from openai import AsyncOpenAI
from .base import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider using Chat Completions API."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("MODEL_NAME", "gpt-4o-mini")
    
    async def generate(self, message: str, context: Dict[str, Any] = None) -> str:
        """Generate response using OpenAI API."""
        try:
            system_prompt = """You are an HR assistant helping employees with leave requests, scheduling, compliance questions, and general HR inquiries. 
Be helpful, professional, and concise. If you need more information, ask clarifying questions."""
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add context if available
            if context:
                if context.get("memory"):
                    messages.append({"role": "system", "content": f"Previous conversation context: {context['memory']}"})
            
            messages.append({"role": "user", "content": message})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Please try again or contact HR directly. Error: {str(e)}"