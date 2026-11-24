# app/dashboard_db.py - conversation log + quiz scores for the student dashboard
import os
import re
import mysql.connector
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

USER_ID = "student_1"

DB_CONFIG = dict(
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE", "student_memory"),
)

_tables_ready = False


def _connect():
    return mysql.connector.connect(**DB_CONFIG)


def init_tables():
    """Create the dashboard tables if they do not exist yet."""
    global _tables_ready
    if _tables_ready:
        return True
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversation_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                question TEXT NOT NULL,
                topic VARCHAR(255) NOT NULL,
                agents VARCHAR(255),
                source VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_date (user_id, created_at)
            )""")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quiz_scores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                topic VARCHAR(255) NOT NULL,
                difficulty VARCHAR(20),
                score INT NOT NULL,
                total INT NOT NULL,
                percentage DECIMAL(5,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_date (user_id, created_at)
            )""")
        conn.commit()
        cur.close()
        conn.close()
        _tables_ready = True
        return True
    except mysql.connector.Error as e:
        print(f"MySQL error (init_tables): {e}", flush=True)
        return False


def _write(query, params):
    if not init_tables():
        return False
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except mysql.connector.Error as e:
        print(f"MySQL error (write): {e}", flush=True)
        return False


def _read(query, params=()):
    """Returns a DataFrame, or None if MySQL is unreachable."""
    if not init_tables():
        return None
    try:
        conn = _connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return pd.DataFrame(rows)
    except mysql.connector.Error as e:
        print(f"MySQL error (read): {e}", flush=True)
        return None


# ---------------------------------------------------------------- topics
_FILLER = re.compile(
    r"\b(what is|what are|what's|explain|tell me|about|give me|create|make|"
    r"write|show me|please|can you|could you|i want|want to|how does|how do|"
    r"works?|learn|know|understand|study plan|study|plan|schedule|timetable|"
    r"roadmap|quiz|mcqs?|practice questions?|questions?|test|\d+\s*-?\s*"
    r"(days?|weeks?|months?)|and|also|then|with|me|my|i|a|an|the|of|on|for|"
    r"in|to|is|are)\b", re.I)

_CANON = {"py": "Python", "ml": "Machine Learning", "ai": "AI", "sql": "SQL",
          "js": "JavaScript", "html": "HTML", "css": "CSS", "oop": "OOP",
          "oops": "OOP", "dsa": "DSA", "cpp": "C++", "dbms": "DBMS"}


def extract_topic(text: str) -> str:
    """Cheap rule-based topic: 'Create a 7-day Python study plan' -> 'Python'."""
    cleaned = _FILLER.sub(" ", text or "")
    cleaned = re.sub(r"[^\w\s+#.-]", " ", cleaned)
    words = cleaned.split()[:4]
    if not words:
        return "General"
    out = []
    for w in words:
        out.append(_CANON.get(w.lower(), w.capitalize()))
    return " ".join(out)


# ---------------------------------------------------------------- writes
def log_conversation(user_id, question, topic=None, agents="", source="agents"):
    """Never raises: logging must not break the assistant."""
    try:
        topic = topic or extract_topic(question)
        _write("INSERT INTO conversation_log (user_id, question, topic, agents, source) "
               "VALUES (%s, %s, %s, %s, %s)",
               (user_id, question.strip()[:2000], topic[:255], agents[:255], source))
    except Exception as e:
        print(f"log_conversation failed: {e}", flush=True)


def log_quiz_score(user_id, topic, difficulty, score, total):
    try:
        pct = round(score * 100.0 / total, 2) if total else 0
        return _write(
            "INSERT INTO quiz_scores (user_id, topic, difficulty, score, total, percentage) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, extract_topic(topic), difficulty, score, total, pct))
    except Exception as e:
        print(f"log_quiz_score failed: {e}", flush=True)
        return False


# ----------------------------------------------------------------- reads
def get_day_conversations(user_id, day):
    return _read(
        "SELECT TIME_FORMAT(created_at, '%H:%i') AS time, topic, question, agents "
        "FROM conversation_log WHERE user_id=%s AND DATE(created_at)=%s "
        "ORDER BY created_at", (user_id, day))


def get_daily_counts(user_id, days=14):
    return _read(
        "SELECT DATE(created_at) AS day, COUNT(*) AS questions "
        "FROM conversation_log WHERE user_id=%s "
        "AND created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY) "
        "GROUP BY DATE(created_at) ORDER BY day", (user_id, days))


def get_quiz_history(user_id, limit=20):
    return _read(
        "SELECT DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') AS taken_at, topic, "
        "difficulty, CONCAT(score, '/', total) AS score, percentage "
        "FROM quiz_scores WHERE user_id=%s ORDER BY created_at DESC LIMIT %s",
        (user_id, limit))


def get_topic_stats(user_id):
    """One row per topic: questions asked + quiz results (avg / best %)."""
    asked = _read(
        "SELECT LOWER(topic) AS k, MIN(topic) AS topic, COUNT(*) AS questions_asked "
        "FROM conversation_log WHERE user_id=%s GROUP BY LOWER(topic)", (user_id,))
    quiz = _read(
        "SELECT LOWER(topic) AS k, MIN(topic) AS quiz_topic, COUNT(*) AS tests_taken, "
        "ROUND(AVG(percentage), 1) AS avg_score, MAX(percentage) AS best_score "
        "FROM quiz_scores WHERE user_id=%s GROUP BY LOWER(topic)", (user_id,))
    if asked is None or quiz is None:
        return None
    if asked.empty and quiz.empty:
        return pd.DataFrame()
    if asked.empty:
        asked = pd.DataFrame(columns=["k", "topic", "questions_asked"])
    if quiz.empty:
        quiz = pd.DataFrame(columns=["k", "quiz_topic", "tests_taken",
                                     "avg_score", "best_score"])
    df = asked.merge(quiz, on="k", how="outer")
    df["topic"] = df["topic"].fillna(df["quiz_topic"])
    df["questions_asked"] = pd.to_numeric(df["questions_asked"]).fillna(0).astype(int)
    df["tests_taken"] = pd.to_numeric(df["tests_taken"]).fillna(0).astype(int)
    for c in ("avg_score", "best_score"):
        df[c] = pd.to_numeric(df[c])
    return df[["topic", "questions_asked", "tests_taken", "avg_score",
               "best_score"]].sort_values("questions_asked", ascending=False)