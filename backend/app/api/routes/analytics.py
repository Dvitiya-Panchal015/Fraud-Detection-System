from typing import Any

from fastapi import APIRouter, HTTPException, status

from ...services.dashboard_service import get_analytics


router = APIRouter(prefix="/api/v1", tags=["analytics"])


@router.get("/analytics", summary="Get dataset and model evaluation analytics")
def analytics() -> dict[str, Any]:
    try:
        return get_analytics()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error