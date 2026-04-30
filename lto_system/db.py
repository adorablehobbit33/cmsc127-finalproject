import os
from dotenv import load_dotenv
import mysql.connector

# Load environment variables
load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def execute_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return True, cursor.rowcount
    except mysql.connector.Error as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def fetch_all(query, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"[ERROR] {e}")
        return []
    finally:
        cursor.close()
        conn.close()
