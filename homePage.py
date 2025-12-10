import streamlit as st
from app.cyber_security.user_db import register_user, authenticate_user, getDBPath

st.set_page_config(page_title="Login / Register", page_icon="", layout="centered")

# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


# --- Already logged in ---
if st.session_state.logged_in:
    st.success(f"You are already logged in as **{st.session_state.username}** ")
    st.info("Click the button below to go straight to your dashboard.")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()


tab_login, tab_register = st.tabs([" Login", " Register"])

# =========================
# LOGIN TAB
# =========================
with tab_login:
    st.subheader("Welcome back")

    st.write("Hello,enter your credentials to access the platform.")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input(
        "Password",
        type="password",
        key="login_password",

    )

    col_login_btn, col_login_help = st.columns([1, 2])
    with col_login_btn:
        login_clicked = st.button("Log in", type="primary")
    with col_login_help:
        st.caption("Don’t have an account yet? Switch to the **Register** tab.")

    if login_clicked:
        if not login_username or not login_password:
            st.error("Please enter both **username** and **password**.")
        else:
            if authenticate_user(login_username, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success(" Login successful! Redirecting to your dashboard...")
                st.switch_page("pages/dashboard.py")
            else:
                st.error(" Invalid username or password.")
                st.info("If you’re new here, create an account in the **Register** tab.")

# =========================
# REGISTER TAB
# =========================
with tab_register:
    st.subheader("Create a new account ")

    st.write("Fill in the form below to create your account.")

    new_username = st.text_input(
        "Choose a username",
        key="reg_username",

    )
    new_password = st.text_input(
        "Choose a password",
        type="password",
        key="reg_password",

    )
    confirm_password = st.text_input(
        "Confirm password",
        type="password",
        key="reg_confirm",

    )



    if st.button("Create account"):
        # Basic validation
        if not new_username or not new_password or not confirm_password:
            st.error("Please fill in **all** fields.")
        elif len(new_password) < 6:
            st.error("Password is too short. Use at least **6 characters**.")
        elif new_password != confirm_password:
            st.error("Passwords do **not** match. Please try again.")
        else:
            result = register_user(new_username, new_password)
            if result["success"]:
                st.success(" Account created successfully! You can now log in from the **Login** tab.")
            else:
                st.error(result["message"])


