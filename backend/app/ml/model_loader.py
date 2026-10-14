import csv
import math
from pathlib import Path
from typing import Any

import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "artifacts" / "models" / "fraud_detection_model.joblib"
THRESHOLD_PATH = PROJECT_ROOT / "artifacts" / "reports" / "threshold_tuning.csv"


def load_model() -> Any:
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Trained fraud model was not found at {MODEL_PATH}. "
            "Run the existing training pipeline to create it."
        )

    return joblib.load(MODEL_PATH)


def load_threshold() -> float:
    if not THRESHOLD_PATH.is_file():
        raise FileNotFoundError(
            f"Threshold tuning results were not found at {THRESHOLD_PATH}."
        )

    with THRESHOLD_PATH.open(newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))

    if not rows or not {"threshold", "f1_score"}.issubset(rows[0]):
        raise ValueError(
            "Threshold tuning results must contain threshold and f1_score columns."
        )

    try:
        candidates = [
            (float(row["f1_score"]), float(row["threshold"]))
            for row in rows
        ]
    except (TypeError, ValueError) as error:
        raise ValueError(
            "Threshold tuning results contain a non-numeric score or threshold."
        ) from error

    if any(
        not math.isfinite(score)
        or not math.isfinite(threshold)
        or not 0 <= score <= 1
        or not 0 <= threshold <= 1
        for score, threshold in candidates
    ):
        raise ValueError(
            "Threshold tuning scores and thresholds must be finite values from 0 to 1."
        )

    return max(candidates, key=lambda candidate: candidate[0])[1]