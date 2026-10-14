
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cleaned_transactions.csv"
)

PLOT_DIR = PROJECT_ROOT / "artifacts" / "plots"
REPORT_DIR = PROJECT_ROOT / "artifacts" / "reports"


def run_eda():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {DATA_PATH}"
        )

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH, low_memory=False)

    print("EDA started successfully")
    print("Dataset shape:", df.shape)

    # 1. Dataset information
    print("\nDataset information:")
    df.info()

    # 2. Missing values
    print("\nMissing values:")
    print(df.isnull().sum())

    # 3. Target distribution
    print("\nFraud distribution:")
    print(df["isFraud"].value_counts())

    print("\nFraud percentage:")
    print(
        (df["isFraud"].value_counts(normalize=True) * 100)
        .round(4)
    )

    # 4. Transaction type counts
    print("\nTransaction types:")
    print(df["type"].value_counts())

    # 5. Summary statistics
    print("\nSummary statistics:")
    print(df.describe().T)

    # Save summary report
    df.describe(include="all").T.to_csv(
        REPORT_DIR / "data_summary.csv"
    )

    # 6. Fraud vs legitimate transactions
    plt.figure(figsize=(7, 5))
    sns.countplot(data=df, x="isFraud")
    plt.title("Fraud vs Legitimate Transactions")
    plt.xlabel("Is Fraud (0 = No, 1 = Yes)")
    plt.ylabel("Number of Transactions")
    plt.tight_layout()
    plt.savefig(
        PLOT_DIR / "fraud_distribution.png",
        dpi=150
    )
    plt.close()

    # 7. Transaction types
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df, x="type")
    plt.title("Transaction Type Distribution")
    plt.xlabel("Transaction Type")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(
        PLOT_DIR / "transaction_types.png",
        dpi=150
    )
    plt.close()

    # 8. Transaction amount distribution
    # Log scale makes highly skewed amounts easier to inspect.
    plt.figure(figsize=(8, 5))
    sns.histplot(
        data=df,
        x="amount",
        bins=60,
        log_scale=(False, True)
    )
    plt.title("Transaction Amount Distribution")
    plt.xlabel("Transaction Amount")
    plt.ylabel("Frequency (log scale)")
    plt.tight_layout()
    plt.savefig(
        PLOT_DIR / "transaction_amount_distribution.png",
        dpi=150
    )
    plt.close()

    # 9. Fraud rate by transaction type
    fraud_rate = (
        df.groupby("type", observed=True)["isFraud"]
        .mean()
        .mul(100)
        .sort_values(ascending=False)
    )

    print("\nFraud rate by transaction type (%):")
    print(fraud_rate.round(4))

    fraud_rate.to_csv(
        REPORT_DIR / "fraud_rate_by_type.csv",
        header=["fraud_percentage"]
    )

    plt.figure(figsize=(8, 5))
    fraud_rate.sort_values().plot(kind="barh")
    plt.title("Fraud Rate by Transaction Type")
    plt.xlabel("Fraud Percentage")
    plt.ylabel("Transaction Type")
    plt.tight_layout()
    plt.savefig(
        PLOT_DIR / "fraud_rate_by_type.png",
        dpi=150
    )
    plt.close()

    print("\nEDA completed successfully!")
    print("Plots saved to:", PLOT_DIR)
    print("Reports saved to:", REPORT_DIR)


if __name__ == "__main__":
    run_eda()