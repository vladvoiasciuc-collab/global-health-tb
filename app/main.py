from fastapi import FastAPI

from app.controllers import observation_controller


def create_app() -> FastAPI:
    app = FastAPI(
        title="Global Health Data Platform",
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
    )
    app.include_router(observation_controller.router)
    return app


app = create_app()
