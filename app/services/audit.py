from typing import List, Dict, Optional
from ..db.database import get_db

class AuditLogger:
    """Append-only audit logging service."""
    
    async def log_request(
        self, 
        user_id: str, 
        request: str, 
        intent: str, 
        agent: str, 
        response: str, 
        status: str
    ) -> None:
        """Log a request/response interaction."""
        async with get_db() as db:
            await db.execute("""
                INSERT INTO audit_logs (user_id, request, intent, agent, response, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, request, intent, agent, response, status))
            await db.commit()
    
    async def get_logs(
        self, 
        user_id: Optional[str] = None, 
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Retrieve audit logs with optional user filtering."""
        async with get_db() as db:
            if user_id:
                cursor = await db.execute("""
                    SELECT * FROM audit_logs 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ? OFFSET ?
                """, (user_id, limit, offset))
            else:
                cursor = await db.execute("""
                    SELECT * FROM audit_logs 
                    ORDER BY timestamp DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

audit_logger = AuditLogger()