
from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "artifacts/models/fraud_detection_model.joblib"
TEST_PATH = PROJECT_ROOT / "data/processed/test.csv.gz"
TUNING_PATH = PROJECT_ROOT / "artifacts/reports/threshold_tuning.csv"

REPORT_DIR = PROJECT_ROOT / "artifacts/reports"
REPORT_PATH = REPORT_DIR / "final_test_evaluation.txt"
CONFUSION_PATH = REPORT_DIR / "test_confusion_matrix.csv"

TARGET = "isFraud"

EXCLUDED_COLUMNS = [
    "isFraud",
    "isFlaggedFraud",
    "nameOrig",
    "nameDest",
]


def main():
    print("Loading trained model...")
    model = joblib.load(MODEL_PATH)

    print("Loading threshold tuning results...")
    tuning_df = pd.read_csv(TUNING_PATH)

    best_row = tuning_df.loc[tuning_df["f1_score"].idxmax()]
    threshold = float(best_row["threshold"])

    print(f"Selected validation threshold: {threshold:.2f}")

    print("Loading test data...")
    test_df = pd.read_csv(TEST_PATH, compression="gzip")

    X_test = test_df.drop(
        columns=[c for c in EXCLUDED_COLUMNS if c in test_df.columns]
    )
    y_test = test_df[TARGET].astype(int)

    print("Test data shape:", X_test.shape)
    print("Calculating predictions...")

    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    precision = precision_score(
        y_test, predictions, zero_division=0
    )
    recall = recall_score(
        y_test, predictions, zero_division=0
    )
    f1 = f1_score(
        y_test, predictions, zero_division=0
    )
    average_precision = average_precision_score(
        y_test, probabilities
    )
    roc_auc = roc_auc_score(y_test, probabilities)

    cm = confusion_matrix(y_test, predictions, labels=[0, 1])

    report = f"""
FINAL FRAUD DETECTION TEST EVALUATION
=====================================
Selected threshold: {threshold:.4f}
Test transactions: {len(y_test)}
Actual fraud transactions: {int(y_test.sum())}

Precision: {precision:.4f}
Recall: {recall:.4f}
F1-score: {f1:.4f}
Average Precision (PR-AUC): {average_precision:.4f}
ROC-AUC: {roc_auc:.4f}

Confusion Matrix:
                  Predicted Legitimate  Predicted Fraud
Actual Legitimate {cm[0, 0]}                 {cm[0, 1]}
Actual Fraud      {cm[1, 0]}                 {cm[1, 1]}

Classification Report:
{classification_report(y_test, predictions, zero_division=0)}
"""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")

    pd.DataFrame(
        cm,
        index=["Actual_Legitimate", "Actual_Fraud"],
        columns=["Predicted_Legitimate", "Predicted_Fraud"],
    ).to_csv(CONFUSION_PATH)

    print(report)
    print("Evaluation report saved to:", REPORT_PATH)
    print("Confusion matrix saved to:", CONFUSION_PATH)
    print("Test evaluation completed successfully!")


if __name__ == "__main__":
    main()
