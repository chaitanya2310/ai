import requests
import streamlit as st

from app.mcq_ui import render_mcq_page
from dashboard.dashboard_ui import render_dashboard_page
from courses.courses_ui import render_courses_page
from login.login_ui import render_login_page, logout_button
from styles.style  import inject_css

API_URL = "http://127.0.0.1:8000"   # same host/port as uvicorn

st.set_page_config(page_title="Student Assistant", page_icon="🎓", layout="wide")
inject_css()

user = render_login_page()
if user is None:
    st.stop()          # nothing else is shown until the student logs in
logout_button()

page = st.sidebar.radio("Menu", ["Ask Assistant", "Courses", "MCQ Test", "Dashboard"])


def ask_page():
    st.title("🎓 Student Assistant")
    question = st.text_area("Ask your question")

    if st.button("Ask Assistant"):
        if not question.strip():
            st.warning("Please enter a question.")
            return
        with st.spinner("Thinking... (local model can take a few minutes)"):
            try:
                r = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question, "user_id": user},
                    timeout=900,
                )
            except requests.exceptions.RequestException as e:
                st.error(f"Cannot reach the API: {e}")
                return

        if r.status_code != 200:
            st.error(f"API error {r.status_code}")
            st.code(r.text)
            return

        data = r.json()
        st.caption(f"Source: {data.get('source')} | "
                   f"Agents: {', '.join(data.get('agents', [])) or '-'}")
        st.markdown(data.get("answer", "No answer returned."))


if page == "Ask Assistant":
    ask_page()
elif page == "Courses":
    render_courses_page()
elif page == "MCQ Test":
    render_mcq_page()
else:
    render_dashboard_page(user)