import streamlit as st
import pandas as pd
from database.db import execute_query
from datetime import datetime
import plotly.express as px


# ----------------------------
# Helper functions
# ----------------------------
def insert_incident(date, incident_type, severity, resolution_time, description, assigned_to=None):
    """Insert new incident into DB."""
    query = """
            INSERT INTO cyber_incidents
            (date, incident_type, severity, resolution_time, description, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?) \
            """
    execute_query(query, (date, incident_type, severity, resolution_time, description, assigned_to))


def get_all_incidents():
    """Get all incidents as DataFrame."""
    return pd.DataFrame(execute_query("SELECT * FROM cyber_incidents ORDER BY id DESC", fetch=True))


# ----------------------------
# Dashboard page
# ----------------------------
def show():
    st.header("Cybersecurity Dashboard")

    if "user" not in st.session_state:
        st.warning("Please log in to access the dashboard.")
        st.stop()

    st.subheader("Add New Incident")
    with st.form("add_incident"):
        incident_type = st.text_input("Incident Type", value="Phishing")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        resolution_time = st.number_input("Resolution Time (hours)", min_value=0.0, step=0.5)
        description = st.text_area("Description")
        assigned_to = st.text_input("Assigned To")
        submitted = st.form_submit_button("Add Incident")

        if submitted:
            insert_incident(
                date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                incident_type=incident_type,
                severity=severity,
                resolution_time=resolution_time,
                description=description,
                assigned_to=assigned_to
            )
            st.success("Incident added successfully!")

    # Load all incidents
    df = get_all_incidents()

    if not df.empty:
        st.subheader("Incident Records")
        st.dataframe(df[["id", "date", "incident_type", "severity", "resolution_time", "assigned_to", "description"]])

        # ----------------------------
        # Visualization 1: Incidents per Day
        # ----------------------------
        st.subheader("Incidents Over Time")
        df["date_only"] = pd.to_datetime(df["date"]).dt.date
        daily_counts = df.groupby("date_only").size().reset_index(name="count")
        fig1 = px.line(daily_counts, x="date_only", y="count", title="Incidents per Day")
        st.plotly_chart(fig1, use_container_width=True)

        # ----------------------------
        # Visualization 2: Avg Resolution Time by Type
        # ----------------------------
        st.subheader("Average Resolution Time by Incident Type")
        avg_rt = df.groupby("incident_type")["resolution_time"].mean().reset_index()
        fig2 = px.bar(avg_rt, x="incident_type", y="resolution_time",
                      title="Avg Resolution Time (hours)")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No incidents available yet.")
