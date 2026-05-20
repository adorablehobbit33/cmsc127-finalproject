import os
import re
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# Build paths relative to this script's location, not the working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SQL_FILES = [
    os.path.join(BASE_DIR, "sql", "setup.sql"),
    os.path.join(BASE_DIR, "sql", "dummy_data.sql")
]

def db_exists(cursor, db_name):
    cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
    return cursor.fetchone() is not None

def run_sql_file(cursor, filepath):
    with open(filepath, "r") as f:
        raw = f.read()

    # Remove full-line and inline -- comments before splitting
    raw = re.sub(r'--[^\n]*', '', raw)

    # Remove /* ... */ block comments
    raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)

    # Split on semicolons, skip blank results
    statements = [s.strip() for s in raw.split(";") if s.strip()]

    for statement in statements:
        try:
            cursor.execute(statement)
        except mysql.connector.Error as e:
            print(f"  [!] Skipped — {e}")

def reset():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        conn.autocommit = True
        cursor = conn.cursor()

        db_name = os.getenv("DB_NAME", "project")
        is_first_run = not db_exists(cursor, db_name)

        print("\n========================================")
        if is_first_run:
            print("   LTO Database Initialization")
            print("========================================")
            print("No existing database found. Setting up for the first time...")
        else:
            print("   LTO Database Reset")
            print("========================================")
            print("Restoring database to original dummy data...")

        for filepath in SQL_FILES:
            label = os.path.basename(filepath)
            print(f"\n  Running {label}...")
            run_sql_file(cursor, filepath)
            print(f"  [✓] {label} done.")

        cursor.close()
        conn.close()

        if is_first_run:
            print("\n[✓] Database initialized and populated. Ready to use.\n")
        else:
            print("\n[✓] Database reset complete. Original data restored.\n")

    except mysql.connector.Error as e:
        print(f"\n[✗] Connection failed: {e}\n")

if __name__ == "__main__":
    reset()