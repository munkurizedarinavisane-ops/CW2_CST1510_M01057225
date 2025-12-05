import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sqlite3

# ============================================================
#  DATABASE CONNECTION
# ============================================================
def connect_database():
    return sqlite3.connect("cyber.db", check_same_thread=False)


# ============================================================
#  ACCESS CONTROL
# ============================================================
# ============================================================
#  ACCESS CONTROL
# ============================================================
# ============================================================
#  ACCESS CONTROL (Fixes ALL NoneType issues)
# ============================================================


# -------- ACCESS CONTROL ----------
user = st.session_state.get("user")

if not user or "username" not in user:
    st.error("You must log in first.")
    st.stop()

st.sidebar.success(f"Logged in as {user['username']}")
if st.sidebar.button("Logout"):
    st.session_state.pop("user", None)
    st.experimental_rerun()

conn = connect_database()
cursor = conn.cursor()


# ============================================================
#  READ DATA FROM DATABASE
# ============================================================
def load_incidents():
    try:
        df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()  # return empty if fails


# ============================================================
#  CREATE NEW INCIDENT (CRUD - Create)
# ============================================================
st.subheader("Create Cyber Incident")

with st.form("create_incident_form"):
    col1, col2 = st.columns(2)

    with col1:
        incident_type = st.selectbox(
            "Incident Type",
            ["Phishing", "Malware", "Ransomware", "DDoS"]
        )

    with col2:
        severity = st.selectbox("Severity", ["Low", "Medium", "High"])

    description = st.text_area("Description")

    submitted = st.form_submit_button("Add Incident")

    if submitted:
        try:
            cursor.execute(
                "INSERT INTO cyber_incidents (type, severity, description) VALUES (?, ?, ?)",
                (incident_type, severity, description)
            )
            conn.commit()
            st.success("Incident added successfully!")
        except Exception as e:
            st.error(f"Error inserting incident: {e}")


# ============================================================
#  DISPLAY TABLE (CRUD - Read)
# ============================================================
st.subheader("All Incidents")
df = load_incidents()

if df.empty:
    st.warning("No incidents in database yet.")
    st.stop()

st.dataframe(df, use_container_width=True)


# ============================================================
#  UPDATE INCIDENT (CRUD - Update)
# ============================================================
st.subheader("Update Incident")

incident_ids = df["id"].tolist()

if len(incident_ids) == 0:
    st.info("No incidents available to update.")
else:
    selected_id = st.selectbox("Choose Incident ID to Update", incident_ids)
    selected_row = df[df["id"] == selected_id].iloc[0]

    new_severity = st.selectbox(
        "New Severity",
        ["Low", "Medium", "High"],
        index=["Low", "Medium", "High"].index(selected_row["severity"])
    )

    if st.button("Update Severity"):
        try:
            cursor.execute(
                "UPDATE cyber_incidents SET severity=? WHERE id=?",
                (new_severity, selected_id)
            )
            conn.commit()
            st.success("Incident updated!")
        except Exception as e:
            st.error(f"Error updating incident: {e}")


# ============================================================
#  DELETE INCIDENT (CRUD - Delete)
# ============================================================
st.subheader("Delete Incident")

if len(incident_ids) == 0:
    st.info("No incidents available to delete.")
else:
    del_id = st.selectbox("Select ID to Delete", incident_ids)

    if st.button("Delete Incident"):
        try:
            cursor.execute("DELETE FROM cyber_incidents WHERE id=?", (del_id,))
            conn.commit()
            st.error("Incident deleted!")
        except Exception as e:
            st.error(f"Error deleting incident: {e}")


# ============================================================
#  VISUALIZATIONS
# ============================================================
st.header("Visualizations")

# Bar chart: Incidents by type
fig1 = px.bar(df, x="type", title="Incidents by Type")
st.plotly_chart(fig1, use_container_width=True)

# Pie chart: Severity breakdown
fig2 = px.pie(df, names="severity", title="Severity Distribution")
st.plotly_chart(fig2, use_container_width=True)

# Trend chart: only if date exists
if "date" in df.columns:
    fig3 = px.line(df, x="date", title="Incidents Over Time")
    st.plotly_chart(fig3, use_container_width=True)


# ============================================================
#  CLOSE CONNECTION
# ============================================================
conn.close()

