# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, webhook  # Import API routers
from app.core.config import settings
from app.core.celery_utils import startup_event  # Import startup event function
import os
import logging

logger = logging.getLogger(__name__)
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Put your startup code here
    webhook.load_events_from_file()  # Load events on startup
    startup_event()  # Celery startup check
    yield
    # Shutdown: Put your cleanup code here
    # This runs when the application is shutting down

app = FastAPI(title="Meta Webhook Server", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router)
app.include_router(webhook.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)  # Configure logging here in main
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # Enable reload for development