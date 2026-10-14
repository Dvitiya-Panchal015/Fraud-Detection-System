from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "step": 1,
                    "amount": 9839.64,
                    "transaction_type": "PAYMENT",
                    "old_balance_origin": 170136.0,
                    "new_balance_origin": 160296.36,
                    "old_balance_destination": 0.0,
                    "new_balance_destination": 0.0,
                }
            ]
        },
    )

    step: int = Field(ge=0, description="Transaction time step")
    amount: float = Field(ge=0, description="Transaction amount")
    transaction_type: Literal[
        "CASH_IN",
        "CASH_OUT",
        "DEBIT",
        "PAYMENT",
        "TRANSFER",
    ] = Field(description="Transaction type supported by the trained model")
    old_balance_origin: float = Field(ge=0)
    new_balance_origin: float = Field(ge=0)
    old_balance_destination: float = Field(ge=0)
    new_balance_destination: float = Field(ge=0)


class PredictionResponse(BaseModel):
    prediction: int = Field(description="0 = legitimate, 1 = fraud")
    fraud_probability: float = Field(ge=0, le=1)
    threshold: float = Field(ge=0, le=1)
    message: str