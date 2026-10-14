
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRAIN_PATH = PROJECT_ROOT / "data" / "processed" / "train.csv.gz"
VALIDATION_PATH = PROJECT_ROOT / "data" / "processed" / "validation.csv.gz"

MODEL_DIR = PROJECT_ROOT / "artifacts" / "models"
REPORT_DIR = PROJECT_ROOT / "artifacts" / "reports"

MODEL_PATH = MODEL_DIR / "fraud_detection_model.joblib"
REPORT_PATH = REPORT_DIR / "validation_report.txt"

MLFLOW_DB = PROJECT_ROOT / "mlflow.db"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LOAD DATA
# ============================================================

def load_data():
    print("\nLoading datasets...")

    if not TRAIN_PATH.exists():
        raise FileNotFoundError(f"Training dataset not found: {TRAIN_PATH}")

    if not VALIDATION_PATH.exists():
        raise FileNotFoundError(
            f"Validation dataset not found: {VALIDATION_PATH}"
        )

    train_df = pd.read_csv(TRAIN_PATH)
    validation_df = pd.read_csv(VALIDATION_PATH)

    print("Training shape:", train_df.shape)
    print("Validation shape:", validation_df.shape)

    for df_name, df in [
        ("Training", train_df),
        ("Validation", validation_df),
    ]:
        if "isFraud" not in df.columns:
            raise ValueError(f"'isFraud' missing from {df_name} dataset.")

    return train_df, validation_df


# ============================================================
# 3. PREPARE FEATURES AND TARGET
# ============================================================

def prepare_data(train_df, validation_df):
    print("\nPreparing features and target...")

    target_column = "isFraud"

    # Exclude target, transaction identifiers and leakage-prone flag.
    excluded_columns = [
        "isFraud",
        "nameOrig",
        "nameDest",
        "isFlaggedFraud",
    ]

    feature_columns = [
        column
        for column in train_df.columns
        if column not in excluded_columns
    ]

    missing_columns = [
        column
        for column in feature_columns
        if column not in validation_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Validation data is missing columns: {missing_columns}"
        )

    X_train = train_df[feature_columns].copy()
    y_train = train_df[target_column].copy()

    X_validation = validation_df[feature_columns].copy()
    y_validation = validation_df[target_column].copy()

    # Identify numeric and categorical columns.
    numerical_features = X_train.select_dtypes(
        include=["number"]
    ).columns.tolist()

    categorical_features = X_train.select_dtypes(
        exclude=["number"]
    ).columns.tolist()

    if not numerical_features and not categorical_features:
        raise ValueError("No usable features found.")

    print("Numerical features:", numerical_features)
    print("Categorical features:", categorical_features)

    print("\nTraining target distribution:")
    print(y_train.value_counts().sort_index())

    print("\nValidation target distribution:")
    print(y_validation.value_counts().sort_index())

    return (
        X_train,
        y_train,
        X_validation,
        y_validation,
        feature_columns,
        numerical_features,
        categorical_features,
    )


# ============================================================
# 4. BUILD PREPROCESSING AND MODEL PIPELINE
# ============================================================

def build_model(numerical_features, categorical_features):
    print("\nBuilding machine learning pipeline...")

    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True,
                ),
            ),
        ]
    )

    preprocessing = ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_pipeline,
                numerical_features,
            ),
            (
                "categorical",
                categorical_pipeline,
                categorical_features,
            ),
        ],
        remainder="drop",
    )

    model = Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            (
                "classifier",
                SGDClassifier(
                    loss="log_loss",
                    class_weight="balanced",
                    max_iter=20,
                    tol=1e-3,
                    random_state=42,
                ),
            ),
        ]
    )

    return model


# ============================================================
# 5. EVALUATE MODEL
# ============================================================

def evaluate_model(model, X_validation, y_validation):
    print("\nEvaluating model on validation data...")

    y_pred = model.predict(X_validation)
    y_probability = model.predict_proba(X_validation)[:, 1]

    metrics = {
        "validation_precision": precision_score(
            y_validation, y_pred, zero_division=0
        ),
        "validation_recall": recall_score(
            y_validation, y_pred, zero_division=0
        ),
        "validation_f1": f1_score(
            y_validation, y_pred, zero_division=0
        ),
        "validation_average_precision": average_precision_score(
            y_validation, y_probability
        ),
        "validation_roc_auc": roc_auc_score(
            y_validation, y_probability
        ),
    }

    print("\n========== VALIDATION METRICS ==========")

    for name, value in metrics.items():
        print(f"{name}: {value:.4f}")

    report = classification_report(
        y_validation,
        y_pred,
        labels=[0, 1],
        target_names=["Legitimate", "Fraud"],
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_validation,
        y_pred,
        labels=[0, 1],
    )

    print("\n========== CLASSIFICATION REPORT ==========")
    print(report)

    print("\n========== CONFUSION MATRIX ==========")
    print(matrix)

    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        file.write("VALIDATION METRICS\n")
        file.write("==================\n")

        for name, value in metrics.items():
            file.write(f"{name}: {value:.4f}\n")

        file.write("\nCLASSIFICATION REPORT\n")
        file.write("=====================\n")
        file.write(report)

        file.write("\nCONFUSION MATRIX\n")
        file.write("================\n")
        file.write(str(matrix))

    print(f"\nValidation report saved: {REPORT_PATH}")

    return metrics


# ============================================================
# 6. MAIN TRAINING FUNCTION
# ============================================================

def main():
    print("=" * 60)
    print("FRAUD DETECTION MODEL TRAINING")
    print("=" * 60)

    # Configure MLflow.
    mlflow.set_tracking_uri(
        f"sqlite:///{MLFLOW_DB.as_posix()}"
    )

    mlflow.set_experiment("Fraud_Detection_Experiments")

    # Load datasets.
    train_df, validation_df = load_data()

    # Prepare features.
    (
        X_train,
        y_train,
        X_validation,
        y_validation,
        feature_columns,
        numerical_features,
        categorical_features,
    ) = prepare_data(train_df, validation_df)

    # Build model.
    model = build_model(
        numerical_features,
        categorical_features,
    )

    with mlflow.start_run(run_name="SGD_Baseline_Model"):

        print("\nTraining model...")
        model.fit(X_train, y_train)

        print("Model training completed successfully.")

        # Evaluate on validation data.
        metrics = evaluate_model(
            model,
            X_validation,
            y_validation,
        )

        # Save the local model.
        joblib.dump(model, MODEL_PATH)

        print(f"\nModel saved successfully: {MODEL_PATH}")

        # Log model parameters.
        mlflow.log_params(
            {
                "model_type": "SGDClassifier",
                "loss": "log_loss",
                "class_weight": "balanced",
                "max_iter": 20,
                "random_state": 42,
                "number_of_features": len(feature_columns),
                "training_rows": len(X_train),
                "validation_rows": len(X_validation),
                "numerical_features": ", ".join(numerical_features),
                "categorical_features": ", ".join(categorical_features),
            }
        )

        # Log validation metrics.
        mlflow.log_metrics(metrics)

        # Log the model.
        mlflow.sklearn.log_model(
            sk_model=model,
            name="fraud_detection_model",
            skops_trusted_types=["numpy.dtype"],
        )

        # Log the validation report.
        mlflow.log_artifact(str(REPORT_PATH))

        print("\nModel and metrics logged to MLflow successfully.")
        print("Experiment: Fraud_Detection_Experiments")
        print("MLflow database:", MLFLOW_DB)

    print("\n" + "=" * 60)
    print("TRAINING PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


# ============================================================
# 7. RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()