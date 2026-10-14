import logging

from fastapi import APIRouter, HTTPException, Request, status

from ...ml.predictor import FraudPredictor, ModelPredictionError
from ...schemas import PredictionResponse, TransactionRequest


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["predictions"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict transaction fraud",
)
def predict_transaction(
    transaction: TransactionRequest,
    request: Request,
) -> PredictionResponse:
    predictor = getattr(request.app.state, "predictor", None)
    if not isinstance(predictor, FraudPredictor):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The fraud detection model is not ready.",
        )

    try:
        return predictor.predict(transaction)
    except ModelPredictionError as error:
        logger.exception("Fraud prediction failed.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The fraud prediction could not be completed.",
        ) from error