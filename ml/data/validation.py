from pathlib import Path
import sys


# --------------------------------------------------
# Project root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------
# Import ingestion.py
# --------------------------------------------------

sys.path.append(str(PROJECT_ROOT))

from ml.data.ingestion import load_data


# --------------------------------------------------
# Required columns
# --------------------------------------------------

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
    "isFlaggedFraud"
]


# --------------------------------------------------
# Validation function
# --------------------------------------------------

def validate_data(df):

    print("\n========== DATA VALIDATION ==========\n")

    # 1. Check shape
    print("1. Dataset Shape:")
    print(df.shape)

    # 2. Check required columns
    print("\n2. Checking required columns...")

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        print("Missing columns:", missing_columns)
        return False

    print("All required columns are present.")

    # 3. Check missing values
    print("\n3. Missing Values:")

    missing_values = df.isnull().sum()

    print(missing_values)

    if missing_values.sum() == 0:
        print("No missing values found.")
    else:
        print("Missing values found.")

    # 4. Check duplicate rows
    print("\n4. Duplicate Rows:")

    duplicate_count = df.duplicated().sum()

    print("Duplicate rows:", duplicate_count)

    # 5. Check target column
    print("\n5. Target Column:")

    print(df["isFraud"].value_counts())

    # 6. Check target values
    print("\n6. Unique Target Values:")

    print(df["isFraud"].unique())

    valid_target_values = set(df["isFraud"].unique()).issubset({0, 1})

    if valid_target_values:
        print("Target values are valid.")
    else:
        print("Invalid target values found.")

    # 7. Check data types
    print("\n7. Data Types:")

    print(df.dtypes)

    print("\n========== VALIDATION COMPLETED ==========\n")

    return True


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    df = load_data()

    validation_result = validate_data(df)

    if validation_result:
        print("DATA VALIDATION PASSED")
    else:
        print("DATA VALIDATION FAILED")