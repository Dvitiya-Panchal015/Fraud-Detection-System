
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cleaned_transactions.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


# Load only the columns needed for modeling.
# Account names and the existing fraud flag are excluded.
REQUIRED_COLUMNS = [
    "step",
    "type",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
]


def prepare_features(df):
    """Create features available from transaction data."""

    df = df.copy()

    # Time-related features
    df["transaction_day"] = df["step"] // 24
    df["transaction_hour"] = df["step"] % 24

    # Transaction amount transformation
    df["log_amount"] = (
        df["amount"].clip(lower=0).map(lambda x: __import__("math").log1p(x))
    )

    # Balance-change features
    df["origin_balance_change"] = (
        df["oldbalanceOrg"] - df["newbalanceOrig"]
    )

    df["destination_balance_change"] = (
        df["newbalanceDest"] - df["oldbalanceDest"]
    )

    # Ratios can help distinguish transactions of different sizes
    df["amount_to_origin_balance"] = (
        df["amount"] / (df["oldbalanceOrg"] + 1)
    )

    # Remove the original time column after deriving its features
    df.drop(columns=["step"], inplace=True)

    return df


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {INPUT_PATH}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading cleaned transaction data...")

    # Read only the necessary columns to reduce memory usage.
    df = pd.read_csv(
        INPUT_PATH,
        usecols=REQUIRED_COLUMNS,
        dtype={
            "step": "int32",
            "type": "category",
            "amount": "float64",
            "oldbalanceOrg": "float64",
            "newbalanceOrig": "float64",
            "oldbalanceDest": "float64",
            "newbalanceDest": "float64",
            "isFraud": "int8",
        },
    )

    print("Original shape:", df.shape)

    # Create features before splitting.
    # These transformations do not learn statistics from the data.
    df = prepare_features(df)

    X = df.drop(columns=["isFraud"])
    y = df["isFraud"]

    print("\nFeatures shape:", X.shape)
    print("\nTarget distribution:")
    print(y.value_counts())

    # First split: 70% training, 30% temporary data
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y,
    )

    # Second split: 15% validation, 15% test
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=42,
        stratify=y_temp,
    )

    # Combine features and target for convenient storage.
    train_df = X_train.copy()
    train_df["isFraud"] = y_train

    val_df = X_val.copy()
    val_df["isFraud"] = y_val

    test_df = X_test.copy()
    test_df["isFraud"] = y_test

    print("\nSaving compressed datasets...")

    train_df.to_csv(
        OUTPUT_DIR / "train.csv.gz",
        index=False,
        compression="gzip",
    )

    val_df.to_csv(
        OUTPUT_DIR / "validation.csv.gz",
        index=False,
        compression="gzip",
    )

    test_df.to_csv(
        OUTPUT_DIR / "test.csv.gz",
        index=False,
        compression="gzip",
    )

    print("\nDataset splitting completed successfully!")

    print("\nTraining shape:", train_df.shape)
    print("Validation shape:", val_df.shape)
    print("Test shape:", test_df.shape)

    print("\nFraud counts by split:")
    for name, split_df in [
        ("Train", train_df),
        ("Validation", val_df),
        ("Test", test_df),
    ]:
        print(f"\n{name}:")
        print(split_df["isFraud"].value_counts())

    print("\nFiles saved in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()