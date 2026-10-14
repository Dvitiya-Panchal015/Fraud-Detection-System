
from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

VALIDATION_PATH = (
    PROJECT_ROOT / "data" / "processed" / "validation.csv.gz"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "models"
    / "fraud_detection_model.joblib"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "artifacts" / "reports" / "threshold_tuning.csv"
)


def main():
    print("Loading trained model...")
    model = joblib.load(MODEL_PATH)

    print("Loading validation data...")
    df = pd.read_csv(VALIDATION_PATH, compression="gzip")

    target = "isFraud"

    excluded_columns = [
        "isFraud",
        "isFlaggedFraud",
        "nameOrig",
        "nameDest",
    ]

    feature_columns = [
        col for col in df.columns
        if col not in excluded_columns
    ]

    X_validation = df[feature_columns]
    y_validation = df[target].astype(int)

    print("Validation shape:", X_validation.shape)

    print("Generating fraud probabilities...")
    probabilities = model.predict_proba(X_validation)[:, 1]

    print(
        "Average Precision (PR-AUC):",
        round(average_precision_score(y_validation, probabilities), 4),
    )

    # Test multiple thresholds on validation data.
    thresholds = [
        0.10, 0.15, 0.20, 0.25, 0.30,
        0.35, 0.40, 0.45, 0.50, 0.60,
        0.70, 0.80, 0.90,
    ]

    results = []

    for threshold in thresholds:
        predictions = (probabilities >= threshold).astype(int)

        precision = precision_score(
            y_validation, predictions, zero_division=0
        )
        recall = recall_score(
            y_validation, predictions, zero_division=0
        )
        f1 = f1_score(
            y_validation, predictions, zero_division=0
        )

        results.append({
            "threshold": threshold,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        })

    results_df = pd.DataFrame(results)

    # Save results.
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(REPORT_PATH, index=False)

    print("\nThreshold comparison:")
    print(results_df.round(4).to_string(index=False))

    # Select the threshold with the highest F1 score.
    best_row = results_df.loc[results_df["f1_score"].idxmax()]

    print("\nBest validation threshold:")
    print("Threshold:", best_row["threshold"])
    print("Precision:", round(best_row["precision"], 4))
    print("Recall:", round(best_row["recall"], 4))
    print("F1-score:", round(best_row["f1_score"], 4))

    print("\nResults saved to:", REPORT_PATH)
    print("Threshold tuning completed successfully!")


if __name__ == "__main__":
    main()