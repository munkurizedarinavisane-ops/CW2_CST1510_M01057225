import sqlite3
import os
import pandas as pd

# -------------------------
# Database Path
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_FILE = os.path.join(BASE_DIR, "data", "CYBER_INCIDENTS.db")
CSV_FILE = os.path.join(BASE_DIR, "data", "CYBER_INCIDENTS.csv")

class CyberIncidentDB:

    def __init__(self, db_path=DB_FILE,csv_path=CSV_FILE):
        self.db_path = db_path
        self.csv_path = csv_path
        self._create_table()

    # ------- Internal connection helper --------
    def _connect(self):
        return sqlite3.connect(self.db_path)

    # ------- Create Table --------
    def _create_table(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS cyber_incidents (
                incident_id INTEGER PRIMARY KEY,
                timestamp TEXT,
                severity TEXT,
                category TEXT,
                status TEXT,
                description TEXT
            )
        ''')
        conn.commit()
        conn.close()

    # ------- CRUD METHODS --------
    def insert(self, row):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('''
            INSERT OR IGNORE INTO cyber_incidents
            (incident_id, timestamp, severity, category, status, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            int(row['incident_id']),
            row['timestamp'],
            row['severity'],
            row['category'],
            row['status'],
            row['description']
        ))
        conn.commit()
        conn.close()

    def update_status(self, incident_id, new_status):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(
            "UPDATE cyber_incidents SET status=? WHERE incident_id=?",
            (new_status, incident_id)
        )
        conn.commit()
        conn.close()

    def delete(self, incident_id):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM cyber_incidents WHERE incident_id=?", (incident_id,))
        conn.commit()
        conn.close()

    # ------- QUERY METHODS --------
    def fetch_all(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM cyber_incidents")
        data = cur.fetchall()
        conn.close()
        return pd.DataFrame(
            data,
            columns=["Incident ID", "Timestamp", "Severity", "Category", "Status", "Description"]
        )

    def phishing_trend(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, COUNT(*) 
            FROM cyber_incidents 
            WHERE lower(category)='phishing'
            GROUP BY timestamp 
            ORDER BY timestamp
        """)
        data = cur.fetchall()
        conn.close()
        return pd.DataFrame(data, columns=["Timestamp", "Count"])

    def unresolved_by_category(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT category, COUNT(*) 
            FROM cyber_incidents 
            WHERE status NOT IN ('Closed','Resolved')
            GROUP BY category 
            ORDER BY COUNT(*) DESC
        """)
        data = cur.fetchall()
        conn.close()
        return pd.DataFrame(data, columns=["Category", "Unresolved"])

    def high_severity_open(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM cyber_incidents
            WHERE status NOT IN ('Closed','Resolved')
              AND severity IN ('High','Critical')
        """)
        data = cur.fetchall()
        conn.close()
        return pd.DataFrame(
            data,
            columns=["Incident ID", "Timestamp", "Severity", "Category", "Status", "Description"]
        )


# =====================================================
# PROCEDURAL WRAPPER FUNCTIONS (Dashboard Compatibility)
# =====================================================

_db = CyberIncidentDB()   # Single global instance


def create_table():
    _db._create_table()


def insert_incident(row):
    _db.insert(row)


def update_incident_status(incident_id, new_status):
    _db.update_status(incident_id, new_status)


def delete_incident(incident_id):
    _db.delete(incident_id)


def get_all_incidents():
    return _db.fetch_all()


def phishing_trend_over_time():
    return _db.phishing_trend()


def unresolved_per_category():
    return _db.unresolved_by_category()


def high_severity_open_incidents():
    return _db.high_severity_open()
