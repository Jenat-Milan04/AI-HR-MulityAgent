import os
import aiosqlite
from typing import AsyncContextManager
from contextlib import asynccontextmanager

DATABASE_PATH = os.getenv("DB_PATH", "./hr_agent.db")

async def init_database():
    """Initialize the SQLite database with required tables."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Short-term memory table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS stm_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Long-term memory table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ltm_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                significance REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Audit log table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT NOT NULL,
                request TEXT NOT NULL,
                intent TEXT,
                agent TEXT,
                response TEXT,
                status TEXT NOT NULL
            )
        """)
        
        await db.commit()

@asynccontextmanager
async def get_db() -> AsyncContextManager[aiosqlite.Connection]:
    """Get database connection with context manager."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db