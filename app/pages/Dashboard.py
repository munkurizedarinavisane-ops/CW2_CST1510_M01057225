import streamlit as st
import pandas as pd
import plotly.express as px
from app.db import connect_database

# ============================================================
#  ACCESS CONTROL
# ============================================================
if "user" not in st.session_state:
    st.error("You must log in first.")
    st.stop()

st.title("Cybersecurity Dashboard")
st.write(f"Welcome, **{st.session_state['user']['username']}**!")

conn = connect_database()
cursor = conn.cursor()


# ============================================================
#  READ DATA FROM DATABASE
# ============================================================
def load_incidents():
    df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
    return df


# ============================================================
#  CREATE NEW INCIDENT (CRUD - Create)
# ============================================================
st.subheader("Create Cyber Incident")

with st.form("create_incident_form"):
    col1, col2 = st.columns(2)

    with col1:
        incident_type = st.selectbox("Incident Type", ["Phishing", "Malware", "Ransomware", "DDoS"])

    with col2:
        severity = st.selectbox("Severity", ["Low", "Medium", "High"])

    description = st.text_area("Description")

    submitted = st.form_submit_button("Add Incident")

    if submitted:
        cursor.execute(
            "INSERT INTO cyber_incidents (type, severity, description) VALUES (?, ?, ?)",
            (incident_type, severity, description)
        )
        conn.commit()
        st.success("Incident added successfully!")


# ============================================================
#  DISPLAY TABLE (CRUD - Read)
# ============================================================
st.subheader("All Incidents")
df = load_incidents()
st.dataframe(df)


# ============================================================
#  UPDATE INCIDENT (CRUD - Update)
# ============================================================
st.subheader("Update Incident")

incident_ids = df["id"].tolist()
selected_id = st.selectbox("Choose Incident ID to Update", incident_ids)

selected_row = df[df["id"] == selected_id].iloc[0]

new_severity = st.selectbox(
    "New Severity",
    ["Low", "Medium", "High"],
    index=["Low", "Medium", "High"].index(selected_row["severity"])
)

if st.button("Update Severity"):
    cursor.execute(
        "UPDATE cyber_incidents SET severity=? WHERE id=?",
        (new_severity, selected_id)
    )
    conn.commit()
    st.success("Incident updated!")


# ============================================================
#  DELETE INCIDENT (CRUD - Delete)
# ============================================================
st.subheader("Delete Incident")

del_id = st.selectbox("Select ID to Delete", incident_ids)

if st.button("Delete Incident"):
    cursor.execute("DELETE FROM cyber_incidents WHERE id=?", (del_id,))
    conn.commit()
    st.error("Incident deleted!")


# ============================================================
#  VISUALIZATIONS
# ============================================================
st.header("Visualizations")

# Bar chart: Incidents by type
fig1 = px.bar(df, x="type", title="Incidents by Type")
st.plotly_chart(fig1)

# Pie chart: Severity breakdown
fig2 = px.pie(df, names="severity", title="Severity Distribution")
st.plotly_chart(fig2)

# Trend chart (if you have a date column)
if "date" in df.columns:
    fig3 = px.line(df, x="date", title="Incidents Over Time")
    st.plotly_chart(fig3)


conn.close()
