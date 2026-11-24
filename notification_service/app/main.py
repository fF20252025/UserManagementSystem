from fastapi import FastAPI

from app.core.config import settings
from app.routers.notification import router as notification_router


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)


app.include_router(notification_router)


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "notification"
    }