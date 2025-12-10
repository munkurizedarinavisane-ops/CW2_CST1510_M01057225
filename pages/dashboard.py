import streamlit as st
import pandas as pd
import os

# ---- Internal imports: your app modules ----
from app.cyber_security.dashboard_utils import load_all_dashboard_data
from app.cyber_security.cyber_incidents import (
    insert_incident,
    update_incident_status,
    delete_incident,
    create_table,                  # Make sure the SQLite table exists
    get_all_incidents,             # Read all incidents from DB
    phishing_trend_over_time,      # Phishing trend from DB
    unresolved_per_category,       # Unresolved incidents per category
    high_severity_open_incidents,  # High/Critical unresolved incidents
)
from app.data_science.dataset_metadata import (
    load_datasets_csv,
    dataset_resource_analysis,
    dataset_source_dependency,
)

# IT Operations: OOP analytics class
from app.it_operations.it_operations import TicketAnalytics

# -------------------------------------------------
# BASIC PAGE CONFIGURATION
# -------------------------------------------------
st.set_page_config(
    page_title="Intelligence Dashboard",
    layout="centered"
)

# -------------------------------------------------
# SIMPLE SESSION / LOGIN CHECK
# -------------------------------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must log in first to access the dashboard.")
    if st.button("Go to Login Page"):
        st.switch_page("homePage")
    st.stop()


st.success(f"Welcome, **{st.session_state.username}**")

st.caption(
    "Use the menu on the left to explore Cyber Security incidents, "
    "Dataset analytics, IT Operations tickets, or manage incidents via CRUD."
)

# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
menu = [
    "Dashboard",
    "Cyber Security",
    "Data Science",
    "IT Operations",
    "CRUD",
    "Need Help/Ai",
    "Logout"
]
choice = st.sidebar.selectbox("Main Menu", menu)

# =================================================
# 1) MAIN DASHBOARD OVERVIEW
# =================================================
if choice == "Dashboard":
    st.subheader("Overview")

    # Load summary data for all three domains
    cyber_df, dataset_df, it_df = load_all_dashboard_data()

    # ---- Cyber Incidents Section ----
    st.markdown("###  Cyber Incidents")
    if not cyber_df.empty:
        st.dataframe(cyber_df, use_container_width=True)
        st.markdown(
            """
            **Dashboard Objective (Cyber):**
            - Spot threat trends (e.g., phishing spike).  
            - Identify which incident category has the biggest unresolved backlog.
            """
        )
    else:
        st.info("`cyber_incidents.csv` is missing or empty.")

    # ---- Dataset Metadata Section ----
    st.markdown("###  Dataset Metadata")
    if not dataset_df.empty:
        st.dataframe(dataset_df, use_container_width=True)
        st.markdown(
            """
            **Dashboard Objective (Data Science):**
            - Analyze dataset size and resource consumption.  
            - Understand which teams upload and depend most on which datasets.
            """
        )
    else:
        st.info("`datasets_metadata.csv` is missing or empty.")

    # ---- IT Tickets Section ----
    st.markdown("### IT Tickets")
    if not it_df.empty:
        st.dataframe(it_df, use_container_width=True)
        st.markdown(
            """
            **Dashboard Objective (IT Operations):**
            - Find where tickets are getting delayed (e.g., “Waiting for User”).  
            - See which stages or staff members cause the longest resolution times.
            """
        )
    else:
        st.info("`it_tickets.csv` is missing or empty.")

# =================================================
# 2) CYBER SECURITY ANALYTICS (FROM SQLITE DB)
# =================================================
elif choice == "Cyber Security":
    st.subheader("Cyber Incident Insights")

    # Ensure the database table exists
    create_table()

    # Fetch all incidents from SQLite
    cyber_df = get_all_incidents()

    if cyber_df.empty:
        st.info("No cyber incidents have been logged yet.")
    else:
        # Clean up column names for consistency
        cyber_df.columns = [c.strip().lower().replace(" ", "_") for c in cyber_df.columns]
        # Expected: incident_id, timestamp, severity, category, status, description

        # ---- Key Metrics ----
        total_incidents = len(cyber_df)
        unresolved_count = len(cyber_df[~cyber_df["status"].isin(["Closed", "Resolved"])])
        phishing_count = len(cyber_df[cyber_df["category"].str.lower() == "phishing"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Logged Incidents", total_incidents)
        col2.metric("Pending/Active Incidents", unresolved_count)
        col3.metric("Phishing Cases", phishing_count)

        # ---- Phishing Incidents Over Time ----
        st.markdown("### Phishing Activity Timeline")
        st.caption(
            "Visualizes the number of phishing incidents over time. "
            "Noticeable spikes may indicate concentrated attack campaigns."
        )
        trend_df = phishing_trend_over_time()
        if not trend_df.empty:
            st.line_chart(trend_df.set_index("Timestamp")["Count"])
        else:
            st.info("No phishing incidents recorded yet.")

        # ---- Operational Bottlenecks by Category ----
        st.markdown("### Categories Causing the Most Delays")
        st.caption(
            "Categories with the most unresolved incidents highlight potential operational bottlenecks."
        )
        bottleneck_df = unresolved_per_category()
        if not bottleneck_df.empty:
            st.bar_chart(bottleneck_df.set_index("Category")["Unresolved"])
        else:
            st.info("All incidents have been resolved! 🎉")

        # ---- Open High/Critical Incidents ----
        st.markdown("### Active High & Critical Incidents")
        st.caption(
            "Shows all High/Critical incidents that are still unresolved. "
            "SOC teams should address these with top priority."
        )
        high_df = high_severity_open_incidents()
        if not high_df.empty:
            st.markdown(
                """
                **Insights:**  
                - Incident prioritization may need review.  
                - Some categories may be overloading analysts.  
                - High-risk threats are not being mitigated quickly enough.  
                """
            )
            st.dataframe(high_df, use_container_width=True)
        else:
            st.success("No active High/Critical incidents. Excellent work!")


# =================================================
# 3) CRUD: MANAGE CYBER INCIDENTS
# =================================================
elif choice == "CRUD":
    st.subheader("Manage Cyber Incidents (CRUD)")

    st.caption("Add new incidents or update/delete existing ones stored in the SQLite database.")

    # Ensure table exists
    create_table()

    crud_action = st.selectbox(
        "Choose an action",
        ["Add Incident", "Update Status", "Delete Incident"]
    )

    # ---- ADD INCIDENT ----
    if crud_action == "Add Incident":
        st.markdown("#### Add New Incident")

        incident_id = st.number_input("Incident ID", min_value=1, step=1)
        timestamp = st.text_input("Timestamp (YYYY-MM-DD HH:MM:SS)")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        category = st.text_input("Category (e.g., Phishing, Malware, DDoS)")
        status = st.selectbox("Status", ["Open", "In Progress", "Closed", "Resolved"])
        description = st.text_area("Short Incident Description")

        if st.button("Save Incident"):
            insert_incident({
                "incident_id": incident_id,
                "timestamp": timestamp,
                "severity": severity,
                "category": category,
                "status": status,
                "description": description
            })
            st.success(" Incident added successfully!")

    # ---- UPDATE INCIDENT STATUS ----
    elif crud_action == "Update Status":
        st.markdown("####  Update Incident Status")

        incident_id = st.number_input("Incident ID to update", min_value=1, step=1, key="update_id")
        new_status = st.selectbox(
            "New Status",
            ["Open", "In Progress", "Closed", "Resolved"],
            key="update_status"
        )

        if st.button("Update Status"):
            update_incident_status(incident_id, new_status)
            st.success(f" Incident {incident_id} status updated to **{new_status}**.")

    # ---- DELETE INCIDENT ----
    elif crud_action == "Delete Incident":
        st.markdown("#### Delete Incident")

        incident_id = st.number_input("Incident ID to delete", min_value=1, step=1, key="delete_id")
        if st.button("Delete Incident"):
            delete_incident(incident_id)
            st.success(f"Incident {incident_id} deleted successfully.")

# =================================================
# 4) DATA SCIENCE: DATASET ANALYTICS
# =================================================
elif choice == "Data Science":
    st.subheader(" Dataset Analytics")

    st.caption("Analyze dataset size, usage, and dependencies to support data governance decisions.")

    # Load dataset metadata from CSV
    df = load_datasets_csv()

    if df.empty:
        st.info("`datasets_metadata.csv` is missing or empty. No dataset analytics available.")
        st.stop()

    # Normalize column names (lowercase etc.)
    df.columns = [c.strip().lower() for c in df.columns]

    # ---- Raw Metadata ----
    st.markdown("###  Raw Dataset Metadata")
    st.dataframe(df, use_container_width=True)

    # ---- 1. Dataset Resource Consumption ----
    st.markdown("## 1️ Dataset Resource Consumption")
    resource_df = dataset_resource_analysis(df)

    st.markdown(
        """
        **What this shows:**
        - How big each dataset is (rows × columns).  
        - Whether it is classified as **Small**, **Medium**, or **Large**.
        """
    )

    st.dataframe(resource_df, width="stretch")

    # The bar chart of size score
    st.markdown("### 1.1 Dataset Size Score Comparison")
    chart_df = resource_df.set_index("name")["dataset_size_score"]
    st.bar_chart(chart_df)

    # ---- 2. Dataset Source Dependency ----
    st.markdown("##  Dataset Source Dependency")
    dependency_df = dataset_source_dependency(df)

    st.markdown(
        """
        **What this shows:**
        - How many datasets each uploader/department owns.  
        - Total rows contributed per uploader.  
        - Average number of columns per dataset.
        """
    )

    st.dataframe(dependency_df, width="stretch")

    st.markdown("### 2.1 Datasets Uploaded per Department")
    upload_chart = dependency_df.set_index("uploaded_by")["datasets_uploaded"]
    st.bar_chart(upload_chart)

# =================================================
# 5) IT OPERATIONS DASHBOARD
# =================================================
elif choice == "IT Operations":
    st.subheader(" IT Operations Dashboard")

    st.caption("Visualize IT ticket performance, bottlenecks, and resolution stages.")
    analytics = TicketAnalytics()
    analytics.show_dashboard()

# =================================================
# 6) HELP / AI ASSISTANT SECTION
# =================================================
# =================================================
# 6) INTERACTIVE AI ASSISTANT
# =================================================
elif choice == "Smart Assistant":
    st.subheader("Your AI Dashboard Companion")

    st.caption(
        "Ask targeted questions about the dashboard, cybersecurity incidents, datasets, or IT operations. "
        "Get clear, context-aware guidance instantly."
    )

    # Import and launch the AI helper page
    from app.help.need_help import show_need_help_page
    show_need_help_page()

# =================================================
# 7) LOGOUT
# =================================================
elif choice == "Logout":
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("You have been logged out successfully.")

