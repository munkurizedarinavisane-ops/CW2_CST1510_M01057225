import os
import pandas as pd

# ===========================================
# Load Dataset Metadata CSV
# ===========================================

def load_datasets_csv():
    """
    Loads datasets_metadata.csv from the /app/data/ directory.
    Returns a DataFrame (empty if file is missing).
    """

    ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(ROOT_DIR, "data", "datasets_metadata.csv")

    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)

            # Guarantee required columns exist to avoid dashboard crashes
            expected_cols = ["dataset_id", "name", "rows", "columns", "uploaded_by", "upload_date"]
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None

            return df

        # Return safe empty DataFrame
        return pd.DataFrame(columns=[
            "dataset_id", "name", "rows", "columns", "uploaded_by", "upload_date"
        ])

    except Exception as e:
        print("Error loading datasets CSV:", e)
        return pd.DataFrame()


# ===========================================
# Dataset Resource Consumption Analysis
# ===========================================

def dataset_resource_analysis(df):
    """
    Calculates resource consumption:
    - dataset_size_score = rows * columns
    - size_category = small / medium / large
    Returns a modified DataFrame (same structure).
    """
    if df.empty:
        return df

    df = df.copy()

    # Avoid crashes if columns are strings/null
    df["rows"] = pd.to_numeric(df["rows"], errors="coerce").fillna(0)
    df["columns"] = pd.to_numeric(df["columns"], errors="coerce").fillna(0)

    df["dataset_size_score"] = df["rows"] * df["columns"]

    df["size_category"] = df["dataset_size_score"].apply(
        lambda x: "Large" if x > 3_000_000 else
                  "Medium" if x > 200_000 else
                  "Small"
    )

    return df


# ===========================================
# Dataset Source Dependency Analysis
# ===========================================

def dataset_source_dependency(df):
    """
    Groups datasets by uploader (department/team).
    Returns a summary DataFrame.
    """
    if df.empty:
        return df

    df = df.copy()

    # Safety: ensure numeric values
    df["rows"] = pd.to_numeric(df["rows"], errors="coerce").fillna(0)
    df["columns"] = pd.to_numeric(df["columns"], errors="coerce").fillna(0)

    summary = (
        df.groupby("uploaded_by")
          .agg({
              "dataset_id": "count",
              "rows": "sum",
              "columns": "mean"
          })
          .rename(columns={
              "dataset_id": "datasets_uploaded",
              "rows": "total_rows",
              "columns": "avg_columns"
          })
          .reset_index()
    )

    return summary


# ===========================================
# Governance & Archiving Recommendations
# ===========================================

def dataset_governance_recommendations(df):
    """
    Returns a list of governance recommendations.
    Depends on size_category generated earlier.
    """

    if df.empty or "size_category" not in df.columns:
        return []

    recommendations = []

    for _, row in df.iterrows():
        size = row.get("size_category", "Small")
        name = row.get("name", "Unknown Dataset")

        if size == "Large":
            recommendations.append(
                f"Dataset '{name}' (Large): Recommend archiving older partitions and applying compression."
            )

        elif size == "Medium":
            recommendations.append(
                f"Dataset '{name}' (Medium): Schedule monthly validation checks for schema drift."
            )

        else:
            recommendations.append(
                f"Dataset '{name}' (Small): Keep in active storage; low governance impact."
            )

    return recommendations