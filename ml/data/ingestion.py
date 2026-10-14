from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "PS_20174392719_1491204439457_log.csv"
)


def load_data():

    df = pd.read_csv(RAW_DATA_PATH)

    print("Dataset loaded successfully")
    print("Shape:", df.shape)

    return df


if __name__ == "__main__":

    df = load_data()

    print("\nFirst 5 rows:")
    print(df.head())