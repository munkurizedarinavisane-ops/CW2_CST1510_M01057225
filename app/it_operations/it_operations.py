import streamlit as st
import pandas as pd
import os

class TicketAnalytics:
    def __init__(self):
        # Path to CSV
        self.file_path = os.path.join("app", "data", "it_tickets.csv")
        self.df = self.load_data()

    def load_data(self):
        if not os.path.exists(self.file_path):
            st.error("it_tickets.csv is missing or empty.")
            return pd.DataFrame()
        df = pd.read_csv(self.file_path)
        df.columns = [c.strip().lower() for c in df.columns]
        return df

    def show_dashboard(self):
        st.subheader("IT Tickets Analytics")

        if self.df.empty:
            st.warning("No ticket data available.")
            return

        # Example: display dataframe in Streamlit
        st.dataframe(self.df, width="stretch")




        st.subheader("IT Tickets Analytics ")

        # KPI: Total tickets
        total_tickets = len(self.df)
        total_open = len(self.df[self.df['status'].str.lower() == 'open'])
        total_waiting_user = len(self.df[self.df['status'].str.lower() == 'waiting for user'])
        total_resolved = len(self.df[self.df['status'].str.lower() == 'resolved'])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Tickets", total_tickets)
        col2.metric("Open Tickets", total_open)
        col3.metric("Waiting for User", total_waiting_user)
        col4.metric("Resolved Tickets", total_resolved)

        # --- Staff causing longest delays ---
        self.plot_avg_resolution_by_staff()

        # --- Status causing longest delays ---
        self.plot_avg_resolution_by_status()

        # --- Ticket counts per staff ---
        self.plot_ticket_counts_by_staff()

    def plot_avg_resolution_by_staff(self):
        df = self.df.copy()
        df['resolution_time_hours'] = pd.to_numeric(df['resolution_time_hours'], errors='coerce')
        avg_resolution = df.groupby('assigned_to')['resolution_time_hours'].mean().reset_index()
        avg_resolution = avg_resolution.sort_values(by='resolution_time_hours', ascending=False)

        st.markdown("### 1. Average Resolution Time by Staff (hours)")
        st.markdown("""
        *Observations:*
        - IT_Support_C has the longest average resolution time, suggesting either complex tickets or workload imbalance.
        - IT_Support_A resolves the highest number of tickets but maintains moderate resolution time.
        - IT_Support_B shows variability depending on ticket priority.
        """)
        if not avg_resolution.empty:
            st.bar_chart(avg_resolution.set_index('assigned_to')['resolution_time_hours'])
        else:
            st.info("No data for staff resolution times.")

    def plot_avg_resolution_by_status(self):
        df = self.df.copy()
        df['resolution_time_hours'] = pd.to_numeric(df['resolution_time_hours'], errors='coerce')
        avg_resolution_status = df.groupby('status')['resolution_time_hours'].mean().reset_index()
        avg_resolution_status = avg_resolution_status.sort_values(by='resolution_time_hours', ascending=False)

        st.markdown("### 2. Average Resolution Time by Status (hours)")
        st.markdown("""
        *Observations:*
        - Tickets with status "Waiting for User" take the longest, confirming that user response delays are a significant bottleneck.
        - "In Progress" and "Open" tickets also contribute to delays but are secondary to Waiting for User.
        """)
        if not avg_resolution_status.empty:
            st.bar_chart(avg_resolution_status.set_index('status')['resolution_time_hours'])
        else:
            st.info("No data for status resolution times.")

    def plot_ticket_counts_by_staff(self):
        df = self.df.copy()
        ticket_counts = df.groupby('assigned_to').size().reset_index(name='ticket_count')
        ticket_counts = ticket_counts.sort_values(by='ticket_count', ascending=False)

        st.markdown("### 3. Ticket Counts per Staff")
        st.markdown("""
        *Observations:*
        - IT_Support_A handles the most tickets but resolves them faster than IT_Support_C, indicating better efficiency or lower complexity tickets.
        - IT_Support_C handles fewer tickets but takes longer, highlighting potential workload or skill mismatch.
        """)
        if not ticket_counts.empty:
            st.bar_chart(ticket_counts.set_index('assigned_to')['ticket_count'])
        else:
            st.info("No ticket count data.")