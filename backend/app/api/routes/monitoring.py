from typing import Any

from fastapi import APIRouter, HTTPException, status
from mlflow.exceptions import MlflowException
from sqlalchemy.exc import SQLAlchemyError

from ...services.dashboard_service import get_monitoring


router = APIRouter(prefix="/api/v1", tags=["monitoring"])


@router.get("/monitoring", summary="Get model and MLflow monitoring status")
def monitoring() -> dict[str, Any]:
    try:
        return get_monitoring()
    except (MlflowException, SQLAlchemyError, OSError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Monitoring information could not be retrieved: {error}",
        ) from error