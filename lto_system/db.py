import os
from dotenv import load_dotenv
import mysql.connector

# Load environment variables
load_dotenv()

# Establish connection to SQL
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# INSERT, UPDATE, DELETE STATEMENTS
def execute_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ()) # cursor object is used to execute SQL commands
        conn.commit() # Save
        return True, cursor.rowcount
    except mysql.connector.Error as e:
        conn.rollback() # Undo changes
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

# SELECT STATEMENTS
def fetch_all(query, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True) # Converts to dictionary for easier functionality, to access by 'column name'
    try:
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"[ERROR] {e}")
        return []
    finally:
        cursor.close()
        conn.close()
