import re
from pathlib import Path
from typing import Any

import numpy as np
import mlflow
import pandas as pd
from mlflow.tracking import MlflowClient

from ..ml.model_loader import MODEL_PATH, PROJECT_ROOT, load_threshold


REPORT_DIR = PROJECT_ROOT / "artifacts" / "reports"
DATA_SUMMARY_PATH = REPORT_DIR / "data_summary.csv"
TYPE_FRAUD_PATH = REPORT_DIR / "fraud_rate_by_type.csv"
TEST_EVALUATION_PATH = REPORT_DIR / "final_test_evaluation.txt"
CONFUSION_MATRIX_PATH = REPORT_DIR / "test_confusion_matrix.csv"
MLFLOW_DB_PATH = PROJECT_ROOT / "mlflow.db"
DRIFT_REFERENCE_PATH = PROJECT_ROOT / "data" / "processed" / "train.csv.gz"
DRIFT_CURRENT_PATH = PROJECT_ROOT / "data" / "processed" / "test.csv.gz"
DRIFT_SAMPLE_SIZE = 50_000
DRIFT_FEATURES = (
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "transaction_day",
    "transaction_hour",
    "type",
)

METRIC_PATTERN = re.compile(
    r"^(Precision|Recall|F1-score|Average Precision \(PR-AUC\)|ROC-AUC):\s*([0-9.]+)$",
    re.MULTILINE,
)


def _require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Required project artifact was not found: {path}")


def _dataset_counts() -> dict[str, int | float]:
    _require_file(DATA_SUMMARY_PATH)
    summary = pd.read_csv(DATA_SUMMARY_PATH, index_col=0)
    try:
        transaction_count = int(summary.at["step", "count"])
        fraud_rate = float(summary.at["isFraud", "mean"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            "The saved dataset summary does not contain the expected PaySim statistics."
        ) from error

    fraud_count = round(transaction_count * fraud_rate)
    return {
        "transaction_count": transaction_count,
        "fraud_count": fraud_count,
        "legitimate_count": transaction_count - fraud_count,
        "fraud_rate": fraud_rate,
    }


def _test_metrics() -> dict[str, float | int]:
    _require_file(TEST_EVALUATION_PATH)
    report = TEST_EVALUATION_PATH.read_text(encoding="utf-8")
    metrics: dict[str, float | int] = {}

    selected_threshold = re.search(r"Selected threshold:\s*([0-9.]+)", report)
    test_count = re.search(r"Test transactions:\s*(\d+)", report)
    fraud_count = re.search(r"Actual fraud transactions:\s*(\d+)", report)
    if not selected_threshold or not test_count or not fraud_count:
        raise ValueError("The saved test evaluation report is incomplete.")

    metrics["threshold"] = float(selected_threshold.group(1))
    metrics["test_transactions"] = int(test_count.group(1))
    metrics["actual_fraud_transactions"] = int(fraud_count.group(1))
    metric_names = {
        "Precision": "precision",
        "Recall": "recall",
        "F1-score": "f1",
        "Average Precision (PR-AUC)": "average_precision",
        "ROC-AUC": "roc_auc",
    }
    for label, value in METRIC_PATTERN.findall(report):
        metrics[metric_names[label]] = float(value)

    if len(metric_names) != sum(name in metrics for name in metric_names.values()):
        raise ValueError("The saved test evaluation report is missing model metrics.")

    return metrics


def _confusion_matrix() -> dict[str, list[int]]:
    _require_file(CONFUSION_MATRIX_PATH)
    matrix = pd.read_csv(CONFUSION_MATRIX_PATH, index_col=0)
    expected_rows = ["Actual_Legitimate", "Actual_Fraud"]
    expected_columns = ["Predicted_Legitimate", "Predicted_Fraud"]
    if list(matrix.index) != expected_rows or list(matrix.columns) != expected_columns:
        raise ValueError("The saved test confusion matrix has an unexpected format.")
    return {
        "actual_legitimate": [int(value) for value in matrix.loc[expected_rows[0]]],
        "actual_fraud": [int(value) for value in matrix.loc[expected_rows[1]]],
    }


def _fraud_rates_by_type() -> list[dict[str, str | float]]:
    _require_file(TYPE_FRAUD_PATH)
    frame = pd.read_csv(TYPE_FRAUD_PATH)
    if not {"type", "fraud_percentage"}.issubset(frame.columns):
        raise ValueError("The fraud-by-type report has an unexpected format.")
    return [
        {"transaction_type": str(row.type), "fraud_rate": float(row.fraud_percentage)}
        for row in frame.itertuples(index=False)
    ]


def get_analytics() -> dict[str, Any]:
    counts = _dataset_counts()
    return {
        "dataset": {
            **counts,
            "source": "PaySim full-dataset summary artifact",
        },
        "test_evaluation": {
            **_test_metrics(),
            "source": "Saved held-out test evaluation",
        },
        "confusion_matrix": _confusion_matrix(),
        "fraud_rates_by_type": _fraud_rates_by_type(),
    }


def _latest_mlflow_metrics() -> dict[str, Any]:
    if not MLFLOW_DB_PATH.is_file():
        return {
            "available": False,
            "message": "The project MLflow tracking database is not present.",
            "metrics": {},
        }

    mlflow.set_tracking_uri(f"sqlite:///{MLFLOW_DB_PATH.as_posix()}")
    client = MlflowClient()
    experiments = client.search_experiments()
    experiment = next(
        (item for item in experiments if item.name == "Fraud_Detection_Experiments"),
        None,
    )
    if experiment is None:
        return {
            "available": False,
            "message": "The fraud detection MLflow experiment is not present.",
            "metrics": {},
        }

    runs = client.search_runs(
        [experiment.experiment_id],
        filter_string="attributes.status = 'FINISHED'",
        order_by=["attributes.start_time DESC"],
        max_results=1,
    )
    if not runs:
        return {
            "available": False,
            "message": "No completed runs were found in the fraud detection experiment.",
            "metrics": {},
        }

    run = runs[0]
    return {
        "available": True,
        "experiment": experiment.name,
        "run_id": run.info.run_id,
        "metrics": {
            key: float(value)
            for key, value in run.data.metrics.items()
        },
    }


def _population_stability_index(
    reference: pd.Series,
    current: pd.Series,
) -> float:
    reference_values = pd.to_numeric(reference, errors="coerce").to_numpy(
        dtype=float
    )
    current_values = pd.to_numeric(current, errors="coerce").to_numpy(dtype=float)
    reference_values = reference_values[np.isfinite(reference_values)]
    current_values = current_values[np.isfinite(current_values)]
    if reference_values.size == 0 or current_values.size == 0:
        raise ValueError("Drift samples must contain finite numeric values.")

    cut_points = np.unique(
        np.quantile(reference_values, np.linspace(0, 1, 11)[1:-1])
    )
    reference_bins = np.searchsorted(cut_points, reference_values, side="right")
    current_bins = np.searchsorted(cut_points, current_values, side="right")
    bin_count = len(cut_points) + 1
    reference_counts = np.bincount(reference_bins, minlength=bin_count).astype(float)
    current_counts = np.bincount(current_bins, minlength=bin_count).astype(float)
    epsilon = 1e-6
    reference_share = np.maximum(reference_counts / reference_values.size, epsilon)
    current_share = np.maximum(current_counts / current_values.size, epsilon)

    return float(
        np.sum(
            (current_share - reference_share)
            * np.log(current_share / reference_share)
        )
    )


def _categorical_psi(
    reference: pd.Series,
    current: pd.Series,
) -> float:
    reference_counts = reference.fillna("<missing>").astype(str).value_counts()
    current_counts = current.fillna("<missing>").astype(str).value_counts()
    categories = reference_counts.index.union(current_counts.index)
    if len(categories) == 0:
        raise ValueError("Drift samples must contain categorical values.")

    reference_share = np.maximum(
        reference_counts.reindex(categories, fill_value=0).to_numpy(dtype=float)
        / len(reference),
        1e-6,
    )
    current_share = np.maximum(
        current_counts.reindex(categories, fill_value=0).to_numpy(dtype=float)
        / len(current),
        1e-6,
    )
    return float(
        np.sum(
            (current_share - reference_share)
            * np.log(current_share / reference_share)
        )
    )


def _dataset_split_drift() -> dict[str, Any]:
    _require_file(DRIFT_REFERENCE_PATH)
    _require_file(DRIFT_CURRENT_PATH)
    reference = pd.read_csv(
        DRIFT_REFERENCE_PATH,
        usecols=list(DRIFT_FEATURES),
        nrows=DRIFT_SAMPLE_SIZE,
        compression="gzip",
    )
    current = pd.read_csv(
        DRIFT_CURRENT_PATH,
        usecols=list(DRIFT_FEATURES),
        nrows=DRIFT_SAMPLE_SIZE,
        compression="gzip",
    )
    if reference.empty or current.empty:
        raise ValueError("Training and test split samples must not be empty.")

    features: list[dict[str, str | float]] = []
    for feature in DRIFT_FEATURES:
        if feature == "type":
            psi = _categorical_psi(reference[feature], current[feature])
            data_type = "categorical"
        else:
            psi = _population_stability_index(
                reference[feature],
                current[feature],
            )
            data_type = "numeric"

        features.append(
            {
                "feature": feature,
                "data_type": data_type,
                "psi": psi,
                "status": (
                    "significant"
                    if psi >= 0.25
                    else "moderate"
                    if psi >= 0.1
                    else "low"
                ),
            }
        )

    overall_status = (
        "significant"
        if any(item["status"] == "significant" for item in features)
        else "moderate"
        if any(item["status"] == "moderate" for item in features)
        else "low"
    )
    return {
        "available": True,
        "status": overall_status,
        "mode": "training_test_split_comparison",
        "reference": "data/processed/train.csv.gz",
        "current": "data/processed/test.csv.gz",
        "reference_sample_size": len(reference),
        "current_sample_size": len(current),
        "features": features,
        "message": (
            "This compares shuffled training and test samples. It is a dataset "
            "consistency check, not live production drift monitoring."
        ),
        "interpretation": (
            "PSI guide: below 0.10 low, 0.10–0.25 moderate, 0.25 or higher "
            "significant. These are screening thresholds, not model-quality guarantees."
        ),
    }


def get_monitoring() -> dict[str, Any]:
    mlflow_status = _latest_mlflow_metrics()
    try:
        threshold = load_threshold()
        threshold_status: dict[str, Any] = {
            "available": True,
            "value": threshold,
        }
    except (FileNotFoundError, ValueError) as error:
        threshold_status = {"available": False, "message": str(error)}

    return {
        "model": {
            "available": MODEL_PATH.is_file(),
            "artifact": str(MODEL_PATH.relative_to(PROJECT_ROOT)),
        },
        "threshold": threshold_status,
        "mlflow": mlflow_status,
        "data_drift": _dataset_split_drift(),
    }


def get_transaction_page(
    page: int,
    page_size: int,
    search: str | None,
    transaction_type: str | None,
    is_fraud: bool | None,
) -> dict[str, Any]:
    dataset_path = PROJECT_ROOT / "data" / "processed" / "test.csv.gz"
    _require_file(dataset_path)

    columns = [
        "type",
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "transaction_day",
        "transaction_hour",
        "isFraud",
    ]
    page_start = (page - 1) * page_size
    page_end = page_start + page_size
    matched_count = 0
    items: list[dict[str, Any]] = []
    search_term = search.strip().casefold() if search else ""
    selected_type = transaction_type.strip().casefold() if transaction_type else ""

    for chunk_start, chunk in _iter_test_transactions(dataset_path, columns):
        chunk.insert(
            0,
            "_source_index",
            range(chunk_start, chunk_start + len(chunk)),
        )
        if selected_type:
            chunk = chunk[chunk["type"].astype(str).str.casefold() == selected_type]
        if is_fraud is not None:
            chunk = chunk[chunk["isFraud"].astype(int) == int(is_fraud)]
        if search_term:
            searchable = (
                chunk["type"].astype(str).str.casefold().str.contains(
                    search_term, regex=False
                )
                | chunk["amount"].astype(str).str.contains(search_term, regex=False)
            )
            chunk = chunk[searchable]

        matches_in_chunk = len(chunk)
        local_start = max(page_start - matched_count, 0)
        local_end = min(page_end - matched_count, matches_in_chunk)
        if local_start < local_end:
            for row in chunk.iloc[local_start:local_end].itertuples(
                index=False,
                name=None,
            ):
                (
                    row_index,
                    transaction_type_value,
                    amount,
                    old_balance_origin,
                    new_balance_origin,
                    old_balance_destination,
                    new_balance_destination,
                    transaction_day,
                    transaction_hour,
                    fraud_label,
                ) = row
                items.append(
                    {
                        "record_id": f"test-row-{int(row_index) + 1}",
                        "step": int(transaction_day) * 24 + int(transaction_hour),
                        "transaction_type": str(transaction_type_value),
                        "amount": float(amount),
                        "old_balance_origin": float(old_balance_origin),
                        "new_balance_origin": float(new_balance_origin),
                        "old_balance_destination": float(old_balance_destination),
                        "new_balance_destination": float(new_balance_destination),
                        "is_fraud": bool(fraud_label),
                    }
                )
        matched_count += matches_in_chunk

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": matched_count,
        "source": "PaySim held-out test split; is_fraud is the recorded label, not a model prediction.",
    }


def _iter_test_transactions(
    dataset_path: Path,
    columns: list[str],
):
    chunk_size = 50_000
    row_offset = 0
    for chunk in pd.read_csv(
        dataset_path,
        usecols=columns,
        chunksize=chunk_size,
        compression="gzip",
    ):
        yield row_offset, chunk
        row_offset += len(chunk)
