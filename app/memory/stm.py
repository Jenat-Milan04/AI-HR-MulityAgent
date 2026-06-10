import os
from typing import List, Dict
from ..db.database import get_db

STM_MAX_ENTRIES = int(os.getenv("STM_MAX_ENTRIES", "10"))

class ShortTermMemory:
    """Short-term memory with ring buffer (last N entries per user)."""
    
    async def add_entry(self, user_id: str, message: str) -> None:
        """Add entry and maintain ring buffer size."""
        async with get_db() as db:
            # Insert new entry
            await db.execute(
                "INSERT INTO stm_entries (user_id, message) VALUES (?, ?)",
                (user_id, message)
            )
            
            # Maintain ring buffer - delete oldest entries if over limit
            await db.execute("""
                DELETE FROM stm_entries 
                WHERE user_id = ? AND id NOT IN (
                    SELECT id FROM stm_entries 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                )
            """, (user_id, user_id, STM_MAX_ENTRIES))
            
            await db.commit()
    
    async def get_entries(self, user_id: str) -> List[Dict]:
        """Get all STM entries for user (most recent first)."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM stm_entries WHERE user_id = ? ORDER BY timestamp DESC",
                (user_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def clear_user_memory(self, user_id: str) -> None:
        """Clear all STM entries for a user."""
        async with get_db() as db:
            await db.execute("DELETE FROM stm_entries WHERE user_id = ?", (user_id,))
            await db.commit()

stm = ShortTermMemory()