import streamlit as st
from app.schema import create_all_tables
from database.db import connect_database

# Ensure tables exist
conn = connect_database()
create_all_tables(conn)
conn.close()

st.set_page_config(page_title="Multi-Domain Intelligence Platform", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Login", "Cybersecurity Dashboard"])

if page == "Login":
    from pages import Login

    Login.show()

elif page == "Cybersecurity Dashboard":
    from models import show
    show()
