
from pydantic import BaseModel, Field, ConfigDict


class TransactionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: int = Field(ge=0, description="Transaction time step")
    amount: float = Field(ge=0, description="Transaction amount")
    transaction_type: str = Field(
        min_length=1,
        description="Transaction type, such as PAYMENT or TRANSFER"
    )
    old_balance_origin: float = Field(ge=0)
    new_balance_origin: float = Field(ge=0)
    old_balance_destination: float = Field(ge=0)
    new_balance_destination: float = Field(ge=0)


class PredictionResponse(BaseModel):
    prediction: int = Field(description="0 = legitimate, 1 = fraud")
    fraud_probability: float = Field(ge=0, le=1)
    message: str
