import os
import re
import mysql.connector
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for Windows support
init(autoreset=True)

load_dotenv()

# Build paths relative to this script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SQL_FILES = [
    os.path.join(BASE_DIR, "sql", "setup.sql"),
    os.path.join(BASE_DIR, "sql", "dummy_data.sql")
]

def print_header():
    print(Fore.CYAN + "╔" + "═" * 58 + "╗")
    print(Fore.CYAN + "║" + Fore.YELLOW + "🔄 LTO DATABASE RESET UTILITY".center(58) + Fore.CYAN + "║")
    print(Fore.CYAN + "╚" + "═" * 58 + "╝")

def print_success(msg):
    print(Fore.GREEN + f"✅ {msg}")

def print_error(msg):
    print(Fore.RED + f"❌ {msg}")

def print_info(msg):
    print(Fore.BLUE + f"ℹ️  {msg}")

def print_warning(msg):
    print(Fore.YELLOW + f"⚠️  {msg}")

def print_divider():
    print(Fore.CYAN + "─" * 60)

def db_exists(cursor, db_name):
    cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
    return cursor.fetchone() is not None

def run_sql_file(cursor, filepath):
    """Execute SQL statements from a file, skipping comments and errors"""
    try:
        with open(filepath, "r", encoding='utf-8') as f:
            raw = f.read()
    except FileNotFoundError:
        print_error(f"File not found: {filepath}")
        return False
    except Exception as e:
        print_error(f"Error reading file: {e}")
        return False

    # Remove comments
    raw = re.sub(r'--[^\n]*', '', raw)
    raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)
    statements = [s.strip() for s in raw.split(";") if s.strip()]

    success_count = 0
    error_count = 0
    
    for statement in statements:
        try:
            cursor.execute(statement)
            success_count += 1
        except mysql.connector.Error as e:
            error_count += 1
            # Only show errors for non-duplicate issues
            if "Duplicate" not in str(e) and "already exists" not in str(e):
                print_warning(f"  Skipped: {e}")
    
    print_info(f"  Executed: {success_count} statements, {error_count} skipped")
    return True

def get_db_connection():
    """Test database connection before proceeding"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "")
        )
        return conn
    except mysql.connector.Error as e:
        print_error(f"Connection failed: {e}")
        print_info("Please check your .env file and make sure MariaDB/MySQL is running.")
        return None

def reset():
    print()
    print_header()
    print()
    
    # Check if SQL files exist
    missing_files = []
    for filepath in SQL_FILES:
        if not os.path.exists(filepath):
            missing_files.append(os.path.basename(filepath))
    
    if missing_files:
        print_error(f"Missing SQL files: {', '.join(missing_files)}")
        print_info(f"Expected location: {BASE_DIR}/sql/")
        return
    
    # Test connection
    conn = get_db_connection()
    if not conn:
        return
    
    conn.autocommit = True
    cursor = conn.cursor()

    db_name = os.getenv("DB_NAME", "project")
    is_first_run = not db_exists(cursor, db_name)

    if is_first_run:
        print(Fore.YELLOW + "📦 FIRST TIME SETUP".center(60))
        print_info("No existing database found. Creating new database...")
    else:
        print(Fore.RED + "⚠️  DATABASE RESET  ⚠️".center(60))
        print_warning("This will DELETE ALL CURRENT DATA and restore to original!")
        print()
        
        # Ask for confirmation before resetting
        confirm = input(Fore.RED + "Type 'RESET' to confirm: " + Style.RESET_ALL)
        if confirm != "RESET":
            print_warning("Reset cancelled. No changes were made.")
            cursor.close()
            conn.close()
            return
    
    print()
    print_divider()
    
    # Run SQL files
    for filepath in SQL_FILES:
        label = os.path.basename(filepath)
        print_info(f"Running {label}...")
        run_sql_file(cursor, filepath)
        print_success(f"{label} completed.")
        print()

    cursor.close()
    conn.close()

    print_divider()
    if is_first_run:
        print_success("Database initialized and populated! Ready to use.")
    else:
        print_success("Database reset complete! Original data restored.")
    
    print_info("You can now run 'python main.py' to start the LTO System.")
    print()

if __name__ == "__main__":
    reset()