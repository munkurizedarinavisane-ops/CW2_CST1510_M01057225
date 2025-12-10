import csv
import os
from app.cyber_security.cyber_incidents import create_table, insert_incident

def load_cyber_incidents(csv_file: str):
    create_table()

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            insert_incident(row)

    print("Cyber incidents loaded successfully.")


if __name__ == "__main__":
    # BASE_DIR points to project root
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    csv_path = os.path.join(BASE_DIR, "data", "cyber_incidents.csv")

    load_cyber_incidents(csv_path)
