
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.analytics import router as analytics_router
from .api.routes.monitoring import router as monitoring_router
from .api.routes.prediction import router as prediction_router
from .api.routes.transactions import router as transactions_router
from .ml.model_loader import load_model, load_threshold
from .ml.predictor import FraudPredictor


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    model = load_model()
    threshold = load_threshold()
    app.state.predictor = FraudPredictor(model, threshold)
    yield

app = FastAPI(
    title="Fraud Detection API",
    description="Machine Learning based Fraud Detection System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):517[3-9]",
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(prediction_router)
app.include_router(analytics_router)
app.include_router(transactions_router)
app.include_router(monitoring_router)


@app.get("/")
def home() -> dict[str, str]:
    return {
        "message": "Fraud Detection API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "healthy",
        "service": "fraud-detection-api",
        "model_ready": hasattr(app.state, "predictor"),
    }
