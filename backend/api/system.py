from fastapi import APIRouter
from loguru import logger
import os
import requests

router = APIRouter(tags=["System"])

@router.get("/health", status_code=200)
def health_check():
    logger.info("Healthcheck endpoint hit")
    return {"status": "ok", "service": "Sentinel Orchestrator Backend"}

@router.get("/system-status")
def get_system_status():
    """Get status of all system components."""
    def check_service_health(url: str, timeout: int = 5) -> dict:
        try:
            health_url = f"{url.rstrip('/')}/health"
            response = requests.get(health_url, timeout=timeout)
            return {
                "status": "online" if response.status_code == 200 else "offline",
                "response_time": response.elapsed.total_seconds(),
                "status_code": response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {"status": "offline", "error": str(e)}

    desktop_status = check_service_health("http://localhost:8001")
    ngrok_status = check_service_health("https://thrush-real-lacewing.ngrok-free.app")
    env = os.getenv("ENV", "development")
    if env == "production":
        railway_status = check_service_health("https://sentinalai-production.up.railway.app")
    else:
        railway_status = {"status": "skipped", "reason": "Not in production environment"}
    return {
        "backend": "online",
        "desktop": desktop_status["status"],
        "ngrok": ngrok_status["status"],
        "railway": railway_status["status"],
        "details": {
            "desktop": desktop_status,
            "ngrok": ngrok_status,
            "railway": railway_status
        }
    } 