from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from ...services.dashboard_service import get_transaction_page


router = APIRouter(prefix="/api/v1", tags=["transactions"])


@router.get("/transactions", summary="Browse labeled PaySim holdout transactions")
def transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    search: str | None = Query(default=None, max_length=100),
    transaction_type: str | None = Query(default=None, max_length=20),
    is_fraud: bool | None = Query(default=None),
) -> dict[str, Any]:
    try:
        return get_transaction_page(
            page=page,
            page_size=page_size,
            search=search,
            transaction_type=transaction_type,
            is_fraud=is_fraud,
        )
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error