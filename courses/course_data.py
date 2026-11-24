# app/courses_data.py - loads and saves courses from data/courses.json
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSES_FILE = os.path.join(BASE_DIR, "data", "courses.json")


def _load_raw():
    if not os.path.exists(COURSES_FILE):
        return {"courses": []}
    with open(COURSES_FILE, encoding="utf-8") as f:
        return json.load(f)


def list_courses():
    return _load_raw().get("courses", [])


def get_course(course_id):
    for course in list_courses():
        if course["id"] == course_id:
            return course
    return None


def make_id(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "course"


def add_course(title, description, level, icon, lessons):
    """Append a course. Returns (ok, message)."""
    title = title.strip()
    if not title:
        return False, "Course title is required."
    data = _load_raw()
    courses = data.setdefault("courses", [])
    course_id = make_id(title)
    if any(c["id"] == course_id for c in courses):
        return False, f"A course with id '{course_id}' already exists."
    clean_lessons = [
        {"title": l["title"].strip(), "content": l["content"].strip()}
        for l in lessons
        if l.get("title", "").strip() and l.get("content", "").strip()
    ]
    if not clean_lessons:
        return False, "Add at least one lesson with a title and content."
    courses.append({
        "id": course_id,
        "title": title,
        "description": description.strip(),
        "level": level,
        "icon": icon.strip() or "📘",
        "lessons": clean_lessons,
    })
    with open(COURSES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True, f"Course '{title}' added."