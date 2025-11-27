import streamlit as st
from app.db import execute_query
import bcrypt


def show():
    st.header("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = execute_query("SELECT * FROM users WHERE username=?", (username,), fetch=True)
        if users:
            user = users[0]
            if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
                st.session_state["user"] = {"username": username, "role": user["role"]}
                st.success(f"Logged in as {username}")
            else:
                st.error("Incorrect password")
        else:
            st.error("User not found")

    if "user" in st.session_state:
        st.write("Current user:", st.session_state.user)
