import math
from typing import Any

import pandas as pd

from ..schemas import TransactionRequest


def prepare_model_input(
    transaction: TransactionRequest,
    model: Any,
) -> pd.DataFrame:
    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is None:
        raise ValueError("The loaded model does not declare its expected feature names.")

    values = {
        "type": transaction.transaction_type,
        "amount": transaction.amount,
        "oldbalanceOrg": transaction.old_balance_origin,
        "newbalanceOrig": transaction.new_balance_origin,
        "oldbalanceDest": transaction.old_balance_destination,
        "newbalanceDest": transaction.new_balance_destination,
        "transaction_day": transaction.step // 24,
        "transaction_hour": transaction.step % 24,
        "log_amount": math.log1p(transaction.amount),
        "origin_balance_change": (
            transaction.old_balance_origin - transaction.new_balance_origin
        ),
        "destination_balance_change": (
            transaction.new_balance_destination
            - transaction.old_balance_destination
        ),
        "amount_to_origin_balance": (
            transaction.amount / (transaction.old_balance_origin + 1)
        ),
    }
    columns = list(feature_names)

    if set(columns) != set(values):
        missing = sorted(set(columns) - set(values))
        unsupported = sorted(set(values) - set(columns))
        raise ValueError(
            "The loaded model's feature schema does not match the API preprocessor. "
            f"Missing values: {missing}; unsupported values: {unsupported}."
        )

    return pd.DataFrame(
        [[values[column] for column in columns]],
        columns=columns,
    )