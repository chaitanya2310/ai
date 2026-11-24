import hashlib
import hmac
import os
import secrets
import re 
import mysql.connector 
from dotenv import load_dotenv
from dashboard.dash_board_db import _connect
load_dotenv()
ITERATIONS=200_00
def init_users_table():
   conn=_connect() 
   cur=conn.cursor()
   cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            full_name VARCHAR(100),
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)



"""
      
   )
   conn.commit()
   cur.close()
   conn.close()
def hash_password(password:str):
   salt=secrets.token_hex(16)
   digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt.encode(),ITERATIONS)
   return f"{salt}${digest.hex()}"
def verify_password(password:str,stored:str):
   try:
      salt,digest_hex=stored.split("$",1)
   except ValueError:
      return False
   digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt.encode(),ITERATIONS)
   return hmac.compare_digest(digest.hex(),digest_hex)

def register_user(username, password, full_name=""):
    """Returns (ok, message)."""
    username = username.strip().lower()
    if not re.fullmatch(r"[a-z0-9_.-]{3,50}", username):
        return False, "Username must be 3-50 characters: letters, numbers, _ . -"
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    try:
        init_users_table()
        conn = _connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, full_name, password_hash) "
                    "VALUES (%s, %s, %s)",
                    (username, full_name.strip(), hash_password(password)))
        conn.commit()
        cur.close()
        conn.close()
        return True, "Account created. You can log in now."
    except mysql.connector.IntegrityError:
        return False, "That username is already taken."

def authenticate(username, password):
    """Returns the username if the login is correct, otherwise None."""
    username = username.strip().lower()
    init_users_table()
    conn = _connect()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT username, password_hash FROM users WHERE username=%s",
                (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row and verify_password(password, row["password_hash"]):
        return row["username"]
    return None

   

if __name__=="__main__":
   password=hash_password("chaitanya")
   print(password)