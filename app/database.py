# app/database.py  -  MySQL exact-answer cache
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def _run(query, params, fetch=False):
    try:
        conn = mysql.connector.connect(
            host="localhost", port=3306, user="root",
            password=os.getenv("MYSQL_PASSWORD"), database="student_memory")
        cur = conn.cursor()
        cur.execute(query, params)
        row = cur.fetchone() if fetch else conn.commit()
        cur.close()
        conn.close()
        return row
    except mysql.connector.Error as e:
        print(f"MySQL error: {e}")
        return None


def save_memory(user_id, question, answer):
    _run("INSERT INTO memory (user_id, memory_text, question, answer) "
         "VALUES (%s, %s, %s, %s)",
         (user_id, answer[:200], question.strip().lower(), answer))


def final_exact_answer(user_id, question):
    row = _run("SELECT answer FROM memory WHERE user_id=%s AND question=%s "
               "ORDER BY id DESC LIMIT 1",
               (user_id, question.strip().lower()), fetch=True)
    return row[0] if row else None