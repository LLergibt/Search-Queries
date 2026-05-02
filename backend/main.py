from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import Base, SessionLocal, engine
from api.v1.routes.search_queries import router as search_queries_router
from infrastructure.seeder import seed_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_db(db, target=settings.seed_target)
    finally:
        db.close()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="Search Queries API",
        version="1.0.0",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000", "https://search-queries.vercel.app"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(search_queries_router)

    return application


app = create_app()
