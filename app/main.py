from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


@app.get("/api/v1/health")
def health():

    return {
        "status": "ok",
        "version": settings.app_version,
    }
