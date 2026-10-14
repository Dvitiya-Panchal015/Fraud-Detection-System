
from pathlib import Path

import pandas as pd

from ml.data.ingestion import load_data


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cleaned_transactions.csv"
)

NUMERIC_COLUMNS = [
    "step",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
    "isFlaggedFraud",
]

REQUIRED_COLUMNS = [
    "step",
    "type",
    "amount",
    "nameOrig",
    "oldbalanceOrg",
    "newbalanceOrig",
    "nameDest",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
    "isFlaggedFraud",
]


def clean_data(df):
    print("Starting data cleaning...")
    print("Original shape:", df.shape)

    # 1. Standardize column names
    df.columns = df.columns.str.strip()

    # 2. Check required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # 3. Convert numeric columns to numeric types
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 4. Remove rows missing required values
    missing_before = int(
        df[REQUIRED_COLUMNS].isna().any(axis=1).sum()
    )

    df.dropna(
        subset=REQUIRED_COLUMNS,
        inplace=True
    )

    print("Rows removed due to missing/invalid required values:",
          missing_before)

    # 5. Remove exact duplicate records
    duplicates_before = int(df.duplicated().sum())

    if duplicates_before:
        df.drop_duplicates(inplace=True)

    print("Exact duplicate rows removed:", duplicates_before)

    # 6. Remove invalid target labels
    valid_target = df["isFraud"].isin([0, 1])
    invalid_target_count = int((~valid_target).sum())

    df.drop(
        index=df.index[~valid_target],
        inplace=True
    )

    print("Rows removed due to invalid target:",
          invalid_target_count)

    # 7. Remove negative transaction amounts
    negative_amount_count = int(
        (df["amount"] < 0).sum()
    )

    df.drop(
        index=df.index[df["amount"] < 0],
        inplace=True
    )

    print("Rows removed due to negative amount:",
          negative_amount_count)

    # 8. Clean categorical text
    for col in ["type", "nameOrig", "nameDest"]:
        df[col] = df[col].astype("string").str.strip()

    # Empty names/types should not be retained
    invalid_text = (
        df[["type", "nameOrig", "nameDest"]]
        .isna()
        .any(axis=1)
        |
        (
            df[["type", "nameOrig", "nameDest"]]
            .eq("")
            .any(axis=1)
        )
    )

    empty_text_count = int(invalid_text.sum())

    df.drop(
        index=df.index[invalid_text],
        inplace=True
    )

    print("Rows removed due to empty transaction text:",
          empty_text_count)

    # 9. Reset index
    df.reset_index(drop=True, inplace=True)

    print("\nCleaning completed.")
    print("Cleaned shape:", df.shape)
    print("Remaining missing values:", df.isna().sum().sum())
    print("Remaining duplicates:", df.duplicated().sum())

    print("\nTarget distribution:")
    print(df["isFraud"].value_counts())

    return df


def main():
    df = load_data()
    cleaned_df = clean_data(df)

    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cleaned_df.to_csv(
        PROCESSED_DATA_PATH,
        index=False
    )

    print("\nCleaned dataset saved to:")
    print(PROCESSED_DATA_PATH)


if __name__ == "__main__":
    main()