import os
from typing import List, Dict
from ..db.database import get_db

LTM_THRESHOLD = float(os.getenv("LTM_SIGNIFICANCE_THRESHOLD", "0.7"))

class LongTermMemory:
    """Long-term memory with significance-based filtering."""
    
    def calculate_significance(self, message: str) -> float:
        """Calculate significance score based on keywords."""
        message_lower = message.lower()
        
        # Base significance
        score = 0.2
        
        # HR-relevant keywords
        keywords = [
            "leave", "vacation", "manager", "policy", "schedule", "meeting",
            "interview", "compliance", "remote", "wfh", "sick", "holiday",
            "annual", "personal", "emergency", "guideline", "rule", "handbook"
        ]
        
        # Add 0.1 for each keyword match (max 1.0)
        for keyword in keywords:
            if keyword in message_lower:
                score += 0.1
        
        return min(score, 1.0)
    
    async def add_entry_if_significant(self, user_id: str, message: str) -> bool:
        """Add entry to LTM if it meets significance threshold."""
        significance = self.calculate_significance(message)
        
        if significance >= LTM_THRESHOLD:
            async with get_db() as db:
                await db.execute(
                    "INSERT INTO ltm_entries (user_id, message, significance) VALUES (?, ?, ?)",
                    (user_id, message, significance)
                )
                await db.commit()
            return True
        return False
    
    async def get_entries(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get LTM entries for user (highest significance first)."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM ltm_entries WHERE user_id = ? ORDER BY significance DESC, timestamp DESC LIMIT ?",
                (user_id, limit)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def clear_user_memory(self, user_id: str) -> None:
        """Clear all LTM entries for a user."""
        async with get_db() as db:
            await db.execute("DELETE FROM ltm_entries WHERE user_id = ?", (user_id,))
            await db.commit()

ltm = LongTermMemory()