import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import items_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    yield
    print("Shutting down...")


app = FastAPI(
    title="FastAPI on k8s",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"syntaxHighlight": False},
    docs_url="/docs",
    redoc_url="/redoc",
)


app.include_router(items_router)


@app.get("/")
def root():
    return {"app": "fastapi-k8s"}


@app.get("/health/live")
def liveness():
    # K8s livenessProbe hits this - is the process alive?
    return {"status": "alive"}


@app.get("/health/ready")
def readiness():
    # K8s readinessProbe hits this - is the app ready to serve traffic?
    # check DB conn, model loaded, etc. here
    return {"status": "ready"}
