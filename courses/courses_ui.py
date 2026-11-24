import os

import pandas as pd
import streamlit as st

from courses.course_data import list_courses, get_course, add_course, BASE_DIR

SELECTED_KEY = "selected_course"


def _open_course(course_id):
    st.session_state[SELECTED_KEY] = course_id


def _close_course():
    st.session_state[SELECTED_KEY] = None


def _render_catalog(courses):
    st.write("Pick a course to see its lessons.")
    cols = st.columns(3)
    for i, course in enumerate(courses):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {course.get('icon', '📘')} {course['title']}")
                st.caption(f"{course.get('level', '')} · "
                           f"{len(course['lessons'])} lessons")
                st.write(course.get("description", ""))
                st.button("Open course", key=f"open_{course['id']}",
                          on_click=_open_course, args=(course["id"],),
                          use_container_width=True)


def _lessons_csv(course):
    rows = [{"course": course["title"], "lesson_no": n,
             "lesson_title": l["title"], "content": l["content"]}
            for n, l in enumerate(course["lessons"], start=1)]
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")


def _render_datasets(course):
    datasets = course.get("datasets", [])
    if not datasets:
        return
    st.subheader("📥 Practice datasets (CSV)")
    for ds in datasets:
        path = os.path.join(BASE_DIR, ds["file"])
        if not os.path.exists(path):
            st.warning(f"Missing file: {ds['file']}")
            continue
        with open(path, "rb") as f:
            st.download_button(f"Download {ds['name']}", data=f.read(),
                               file_name=os.path.basename(path), mime="text/csv",
                               key=f"dl_{course['id']}_{ds['file']}")
        with st.expander(f"Preview: {ds['name']}"):
            st.dataframe(pd.read_csv(path).head(10), hide_index=True)


def _render_course(course):
    st.button("← Back to all courses", on_click=_close_course)
    level = course.get("level", "")
    level_cls = f"badge-level-{level.lower()}" if level else ""
    st.markdown(
        f"""<div class="course-hero">
              <h1>{course.get('icon', '📘')} {course['title']}</h1>
              <p>{course.get('description', '')}</p>
              <div style="margin-top:0.8rem">
                <span class="badge {level_cls}">{level}</span>
                <span class="badge badge-lessons">{len(course['lessons'])} lessons</span>
              </div>
            </div>""",
        unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    c1.download_button("📄 Download lessons (CSV)", data=_lessons_csv(course),
                       file_name=f"{course['id']}_lessons.csv", mime="text/csv",
                       key=f"lessons_csv_{course['id']}")
    st.divider()
    _render_datasets(course)
    if course.get("datasets"):
        st.divider()

    for n, lesson in enumerate(course["lessons"], start=1):
        with st.expander(f"Lesson {n}: {lesson['title']}",
                         expanded=(n == 1)):
            st.markdown(lesson["content"])


def _render_add_form():
    with st.expander("➕ Add a new course"):
        with st.form("add_course_form", clear_on_submit=True):
            title = st.text_input("Course title", key="new_title")
            description = st.text_input("Short description", key="new_desc")
            c1, c2 = st.columns(2)
            level = c1.selectbox("Level", ["Beginner", "Intermediate", "Advanced"], key="new_level")
            icon = c2.text_input("Emoji icon", value="📘", key="new_icon")
            n_lessons = st.number_input("Number of lessons", 1, 10, 1, key="new_n")
            lessons = []
            for i in range(int(n_lessons)):
                st.markdown(f"**Lesson {i + 1}**")
                lessons.append({
                    "title": st.text_input("Lesson title", key=f"lt_{i}"),
                    "content": st.text_area(
                        "Lesson content (Markdown, code in ``` blocks)",
                        key=f"lc_{i}", height=120),
                })
            submitted = st.form_submit_button("Save course")

        if submitted:
            ok, msg = add_course(title, description, level, icon, lessons)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


def render_courses_page():
    st.title("📚 Courses")

    if SELECTED_KEY not in st.session_state:
        st.session_state[SELECTED_KEY] = None

    course_id = st.session_state[SELECTED_KEY]
    course = get_course(course_id) if course_id else None

    if course:
        _render_course(course)
    else:
        courses = list_courses()
        if not courses:
            st.info("No courses yet. Add one below.")
        else:
            _render_catalog(courses)
        st.divider()
        _render_add_form()