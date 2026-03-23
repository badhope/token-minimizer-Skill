"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from wealth.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Wealth API starting up...")
    yield
    logger.info("Wealth API shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Wealth API",
        description="Quantitative Analysis Platform for Stocks and Funds",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api/v1")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "wealth.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
