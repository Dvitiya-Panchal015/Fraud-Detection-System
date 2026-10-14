from pathlib import Path
import sys
import pandas as pd


# --------------------------------------------------
# Project root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT))


# --------------------------------------------------
# Import ingestion
# --------------------------------------------------

from ml.data.ingestion import load_data


# --------------------------------------------------
# Numeric columns
# --------------------------------------------------

NUMERIC_COLUMNS = [
    "step",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
    "isFlaggedFraud"
]


# --------------------------------------------------
# Categorical columns
# --------------------------------------------------

CATEGORICAL_COLUMNS = [
    "type",
    "nameOrig",
    "nameDest"
]


# --------------------------------------------------
# Preprocessing function
# --------------------------------------------------

def preprocess_data(df):

    print("\n========== DATA PREPROCESSING ==========\n")

    # Make a copy
    df = df.copy()

    print("Original shape:", df.shape)

    # --------------------------------------------------
    # 1. Remove duplicate rows
    # --------------------------------------------------

    duplicate_count = df.duplicated().sum()

    print("\nDuplicate rows:", duplicate_count)

    if duplicate_count > 0:

        df = df.drop_duplicates()

        print("Duplicates removed.")

    else:

        print("No duplicates to remove.")

    # --------------------------------------------------
    # 2. Check missing values
    # --------------------------------------------------

    print("\nMissing values before cleaning:")

    print(df.isnull().sum())

    # --------------------------------------------------
    # 3. Handle missing numeric values
    # --------------------------------------------------

    for column in NUMERIC_COLUMNS:

        if column in df.columns:

            if df[column].isnull().sum() > 0:

                df[column] = df[column].fillna(
                    df[column].median()
                )

    # --------------------------------------------------
    # 4. Handle missing categorical values
    # --------------------------------------------------

    for column in CATEGORICAL_COLUMNS:

        if column in df.columns:

            if df[column].isnull().sum() > 0:

                df[column] = df[column].fillna("UNKNOWN")

    # --------------------------------------------------
    # 5. Convert numeric columns
    # --------------------------------------------------

    for column in NUMERIC_COLUMNS:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------
    # 6. Convert categorical columns to string
    # --------------------------------------------------

    for column in CATEGORICAL_COLUMNS:

        if column in df.columns:

            df[column] = df[column].astype(str)

    # --------------------------------------------------
    # 7. Remove rows where target is missing
    # --------------------------------------------------

    if "isFraud" in df.columns:

        before = len(df)

        df = df.dropna(subset=["isFraud"])

        after = len(df)

        print(
            "\nRows removed because target was missing:",
            before - after
        )

    # --------------------------------------------------
    # 8. Reset index
    # --------------------------------------------------

    df = df.reset_index(drop=True)

    # --------------------------------------------------
    # Final information
    # --------------------------------------------------

    print("\nFinal shape:", df.shape)

    print("\nMissing values after cleaning:")

    print(df.isnull().sum())

    print("\nData types after preprocessing:")

    print(df.dtypes)

    print("\n========== PREPROCESSING COMPLETED ==========\n")

    return df


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    df = load_data()

    cleaned_df = preprocess_data(df)

    print("\nFirst 5 rows after preprocessing:")

    print(cleaned_df.head())