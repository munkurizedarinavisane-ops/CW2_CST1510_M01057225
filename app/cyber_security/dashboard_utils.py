import os
import pandas as pd

# ----------------------------
# Functions for Dashboard CSVs
# ----------------------------

def load_all_dashboard_data():
    """
    Returns three DataFrames for the Dashboard overview:
    1. cyber_incidents.csv
    2. datasets_metadata.csv
    3. it_tickets.csv
    """
    ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  # fixed
    DATA_DIR = os.path.join(ROOT_DIR, "data")

    # --- 1. cyber_incidents CSV ---
    cyber_csv = os.path.join(DATA_DIR, "cyber_incidents.csv")
    cyber_df = pd.read_csv(cyber_csv) if os.path.exists(cyber_csv) else pd.DataFrame()

    # --- 2. datasets_metadata CSV ---
    dataset_file = os.path.join(DATA_DIR, "datasets_metadata.csv")
    dataset_df = pd.read_csv(dataset_file) if os.path.exists(dataset_file) else pd.DataFrame()

    # --- 3. it_tickets CSV ---
    it_file = os.path.join(DATA_DIR, "it_tickets.csv")
    it_df = pd.read_csv(it_file) if os.path.exists(it_file) else pd.DataFrame()

    return cyber_df, dataset_df, it_df

# ----------------------------
# Function for Cyber Security analytics
# ----------------------------

def load_cyber_incidents_csv():
    """
    Load cyber_incidents.csv specifically for Cyber Security analytics.
    Returns a DataFrame or empty DataFrame if the file does not exist.
    """
    ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
    csv_file = os.path.join(ROOT_DIR, "data", "cyber_incidents.csv")
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        # Ensure consistent lowercase columns for easy filtering
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    return pd.DataFrame()
