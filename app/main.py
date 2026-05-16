from fastapi import FastAPI

from app.api import devices, readings, users
from app.core.config import get_settings
from app.db.session import Base, engine

settings = get_settings()


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name, version="1.0.0")
    application.include_router(users.router)
    application.include_router(devices.router)
    application.include_router(readings.router)

    @application.on_event("startup")
    def on_startup() -> None:
        # Создание таблиц при старте сервиса для упрощения развертывания.
        Base.metadata.create_all(bind=engine)

    @application.get("/health", tags=["system"])
    def health() -> dict:
        return {"status": "ok"}

    return application


app = create_app()
