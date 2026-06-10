from typing import Dict, Tuple

class IntentClassifier:
    """Classify user intents based on keyword matching."""
    
    def __init__(self):
        self.intent_keywords = {
            "SCHEDULING": ["schedule", "meeting", "interview", "calendar", "book", "reschedule", "slot"],
            "LEAVE": ["leave", "vacation", "day off", "sick", "absence", "holiday", "annual leave"],
            "COMPLIANCE": ["policy", "rule", "compliance", "remote work", "wfh", "guideline"]
        }
    
    def classify(self, message: str) -> Tuple[str, float]:
        """
        Classify message intent and return (intent, confidence).
        Returns CLARIFICATION if confidence < 0.5.
        """
        message_lower = message.lower()
        
        # Calculate scores for each intent
        scores = {}
        for intent, keywords in self.intent_keywords.items():
            base_score = 0.4
            keyword_matches = sum(1 for keyword in keywords if keyword in message_lower)
            score = min(base_score + (keyword_matches * 0.15), 0.98)
            scores[intent] = score
        
        # Get highest scoring intent
        if not scores:
            return "CLARIFICATION", 0.2
        
        best_intent = max(scores.keys(), key=lambda k: scores[k])
        confidence = scores[best_intent]
        
        # Use clarification if confidence is too low
        if confidence < 0.5:
            return "CLARIFICATION", confidence
        
        return best_intent, confidence

classifier = IntentClassifier()