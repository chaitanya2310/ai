import streamlit as st

from login.auth_db import register_user, authenticate


def render_login_page():
    """Shows the login/register form. Returns the username once logged in."""
    if st.session_state.get("user"):
        return st.session_state["user"]

    st.title("🎓 Student Assistant")
    login_tab, register_tab = st.tabs(["Log in", "Create account"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")
        if submitted:
            if not username or not password:
                st.error("Enter your username and password.")
            else:
                try:
                    user = authenticate(username, password)
                except Exception as e:
                    st.error(f"Cannot reach the database: {e}")
                    return None
                if user:
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error("Wrong username or password.")

    with register_tab:
        with st.form("register_form"):
            full_name = st.text_input("Full name")
            new_user = st.text_input("Choose a username")
            new_pass = st.text_input("Choose a password (6+ characters)",
                                     type="password")
            confirm = st.text_input("Confirm password", type="password")
            created = st.form_submit_button("Create account")
        if created:
            if new_pass != confirm:
                st.error("Passwords do not match.")
            else:
                try:
                    ok, msg = register_user(new_user, new_pass, full_name)
                except Exception as e:
                    st.error(f"Cannot reach the database: {e}")
                    return None
                (st.success if ok else st.error)(msg)
    return None


def logout_button():
    with st.sidebar:
        st.caption(f"Logged in as **{st.session_state.get('user', '')}**")
        if st.button("Log out"):
            st.session_state.clear()
            st.rerun()