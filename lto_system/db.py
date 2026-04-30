import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="project"
    )

def execute_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return True, "Success"
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