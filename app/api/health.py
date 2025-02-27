# app/api/health.py
from fastapi import APIRouter
import time
from datetime import datetime
import psutil

router = APIRouter()
START_TIME = time.time()

@router.get("/ping")
def ping():
    return {"message": "Server is active"}

@router.get("/health")
async def health_check():
    """Check server health status."""
    uptime_seconds = int(time.time() - START_TIME)
    system_stats = {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": uptime_seconds,
        "system_metrics": system_stats
    }