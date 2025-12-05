import streamlit as st
from services.user_service import authenticate_user

def show():
    st.title("Login")

    # Input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate_user(username, password)

        if user:
            # Store session data
            st.session_state["user"] = {
                "username": username,
                "role": user["role"]
            }

            st.success("Login successful!")

            # Redirect to dashboard
            st.switch_page("pages/Dashboard.py")
        else:
            st.error("Invalid username or password")


if "user" in st.session_state:
    st.sidebar.success(f"Logged in as {st.session_state['user']['username']}")
    if st.sidebar.button("Logout"):
        st.session_state.pop("user", None)
        st.experimental_rerun()
