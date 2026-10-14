import math
from typing import Any

from ..schemas import PredictionResponse, TransactionRequest
from .preprocessor import prepare_model_input


class ModelPredictionError(RuntimeError):
    """Raised when the loaded model cannot return a valid fraud score."""


class FraudPredictor:
    def __init__(self, model: Any, threshold: float) -> None:
        classes = getattr(model, "classes_", None)
        if classes is None or 1 not in classes:
            raise ValueError("The loaded model does not support the fraud class (1).")
        if not callable(getattr(model, "predict_proba", None)):
            raise ValueError("The loaded model does not provide fraud probabilities.")
        if getattr(model, "feature_names_in_", None) is None:
            raise ValueError("The loaded model does not declare its expected features.")
        if not math.isfinite(threshold) or not 0 <= threshold <= 1:
            raise ValueError("The fraud threshold must be a finite value from 0 to 1.")

        self.model = model
        self.threshold = threshold
        self.fraud_class_index = list(classes).index(1)

    def predict(self, transaction: TransactionRequest) -> PredictionResponse:
        try:
            model_input = prepare_model_input(transaction, self.model)
            probabilities = self.model.predict_proba(model_input)
        except (TypeError, ValueError) as error:
            raise ModelPredictionError(
                "The model could not process the transaction features."
            ) from error

        try:
            fraud_probability = float(probabilities[0][self.fraud_class_index])
        except (IndexError, TypeError) as error:
            raise ModelPredictionError(
                "The model returned probabilities in an unexpected format."
            ) from error

        if not math.isfinite(fraud_probability) or not 0 <= fraud_probability <= 1:
            raise ModelPredictionError(
                "The model returned a probability outside the valid range."
            )

        prediction = int(fraud_probability >= self.threshold)
        message = (
            "Transaction flagged as potentially fraudulent."
            if prediction
            else "Transaction classified as legitimate."
        )
        return PredictionResponse(
            prediction=prediction,
            fraud_probability=fraud_probability,
            threshold=self.threshold,
            message=message,
        )