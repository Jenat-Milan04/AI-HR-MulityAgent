import os
from dotenv import load_dotenv
# Load environment variables FIRST before anything else
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .db.database import init_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_database()
    yield

app = FastAPI(
    title="HR Multi-Agent Task Routing & Memory Engine",
    description="A production-ready multi-agent HR automation system built with FastAPI + LangGraph",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)