"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from routes import edges, nodes, routes as route_modules

import models  # noqa: F401 — register ORM models on Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Network Route Optimization API",
    description="Manage network nodes and edges; route optimization to follow.",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
app.include_router(edges.router, prefix="/edges", tags=["edges"])
app.include_router(route_modules.router, prefix="/routes", tags=["routes"])


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "unavailable",
            },
        ) from None
    return {"status": "ok", "database": "ok"}


@app.get("/docs", include_in_schema=False)
def redirect_legacy_docs():
    return RedirectResponse(url="/api/docs", status_code=307)


@app.get("/openapi.json", include_in_schema=False)
def redirect_legacy_openapi():
    return RedirectResponse(url="/api/openapi.json", status_code=307)
