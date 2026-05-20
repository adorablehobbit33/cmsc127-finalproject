from db import execute_query, fetch_all
from colorama import Fore, Style
from db import execute_query, fetch_all
from utils.design import (
    print_header, print_success, print_error, print_info, print_warning,
    print_table, print_divider, print_subheader, input_required,
    input_option, input_date, input_license_number
)


from db import execute_query, fetch_all
from utils.design import (
    print_header, print_success, print_error, print_info, print_warning,
    print_table, print_divider, print_subheader, input_required,
    input_option, input_date, input_license_number
)

def driver_menu():
    while True:
        print_header("DRIVER MANAGEMENT")
        print(Fore.WHITE + """
  ┌────────────────────────────────────────────────────┐
  │  1. Add Driver                                     │
  │  2. Update Driver                                  │
  │  3. Delete Driver                                  │
  │  4. Search Driver                                  │
  │  0. Back to Main Menu                              │
  └────────────────────────────────────────────────────┘
        """)
        
        choice = input(f"{Fore.YELLOW}Enter choice:{Style.RESET_ALL} ").strip()

        if choice == "1":
            add_driver()
        elif choice == "2":
            update_driver()
        elif choice == "3":
            delete_driver()
        elif choice == "4":
            search_driver()
        elif choice == "0":
            break
        else:
            print_error("Invalid choice.")
            input("Press Enter to continue...")

def add_driver():
    print_subheader("ADD NEW DRIVER")
    
    license_number = input_license_number()
    
    # Check if license number already exists
    existing = fetch_all("SELECT license_number FROM driver WHERE license_number = %s", (license_number,))
    if existing:
        print_error(f"License number {license_number} already exists!")
        input("Press Enter to continue...")
        return
    
    first_name = input_required("First Name: ", "First name")
    middle_name = input(f"{Fore.CYAN}Middle Name (leave blank if none):{Style.RESET_ALL} ").strip() or None
    last_name = input_required("Last Name: ", "Last name")
    date_of_birth = input_date("Date of Birth (YYYY-MM-DD): ")
    sex = input_option("Sex:", ["Male", "Female"])
    address = input_required("Address: ", "Address")
    license_type = input_option("License Type:", ["Student Permit", "Non-Professional", "Professional"])
    license_status = input_option("License Status:", ["valid", "expired", "suspended", "revoked"])

    query = """
        INSERT INTO driver (license_number, first_name, middle_name, last_name,
            date_of_birth, sex, address, license_type, license_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    success, msg = execute_query(query, (
        license_number, first_name, middle_name, last_name,
        date_of_birth, sex, address, license_type, license_status
    ))

    if success:
        print_success(f"Driver {first_name} {last_name} added successfully!")
    else:
        print_error(f"Failed: {msg}")
    
    input("\nPress Enter to continue...")

def update_driver():
    print_subheader("UPDATE DRIVER")
    license_number = input_license_number()

    rows = fetch_all("SELECT * FROM driver WHERE license_number = %s", (license_number,))
    if not rows:
        print_error("Driver not found.")
        input("Press Enter to continue...")
        return

    d = rows[0]
    print_info(f"Current info: {d['first_name']} {d['last_name']} | {d['license_type']} | {d['license_status']}")
    print_info("(Press Enter to keep current value)\n")

    address = input(f"{Fore.CYAN}Address [{d['address']}]:{Style.RESET_ALL} ").strip() or d['address']
    license_type = input(f"{Fore.CYAN}License Type [{d['license_type']}]:{Style.RESET_ALL} ").strip() or d['license_type']
    license_status = input(f"{Fore.CYAN}License Status [{d['license_status']}]:{Style.RESET_ALL} ").strip() or d['license_status']

    query = """
        UPDATE driver
        SET address = %s, license_type = %s, license_status = %s
        WHERE license_number = %s
    """
    success, msg = execute_query(query, (address, license_type, license_status, license_number))

    if success:
        print_success("Driver updated successfully.")
    else:
        print_error(f"Failed: {msg}")
    
    input("\nPress Enter to continue...")

def delete_driver():
    print_subheader("DELETE DRIVER")
    license_number = input_license_number()

    rows = fetch_all("SELECT * FROM driver WHERE license_number = %s", (license_number,))
    if not rows:
        print_error("Driver not found.")
        input("Press Enter to continue...")
        return

    d = rows[0]
    print_warning(f"⚠️  You are about to delete: {d['first_name']} {d['last_name']}")
    
    confirm = input(f"{Fore.RED}Type 'DELETE' to confirm:{Style.RESET_ALL} ").strip()
    if confirm != "DELETE":
        print_warning("Cancelled.")
        input("Press Enter to continue...")
        return

    success, msg = execute_query("DELETE FROM driver WHERE license_number = %s", (license_number,))
    if success:
        print_success("Driver deleted successfully.")
    else:
        print_error(f"Failed: {msg}")
    
    input("\nPress Enter to continue...")

def search_driver():
    print_subheader("SEARCH DRIVER")
    print_info("Search by license number, first name, or last name (partial matches allowed)")
    
    keyword = input(f"{Fore.CYAN}Enter name or license number to search:{Style.RESET_ALL} ").strip()
    
    if not keyword:
        print_warning("Please enter a search term")
        input("Press Enter to continue...")
        return
    
    like = f"%{keyword}%"

    query = """
        SELECT license_number,
               CONCAT(first_name, ' ', COALESCE(middle_name, ''), ' ', last_name) AS full_name,
               license_type, license_status, sex, date_of_birth, address
        FROM driver
        WHERE license_number LIKE %s
           OR first_name LIKE %s
           OR last_name LIKE %s
        ORDER BY license_number
    """
    rows = fetch_all(query, (like, like, like))

    if not rows:
        print_warning(f"No drivers found matching '{keyword}'")
        input("Press Enter to continue...")
        return

    headers = ["License No", "Full Name", "Type", "Status", "Sex", "DOB", "Address"]
    data = []
    for r in rows:
        data.append((
            r['license_number'],
            r['full_name'],
            r['license_type'],
            r['license_status'],
            r['sex'],
            r['date_of_birth'],
            r['address'][:40] + "..." if len(r['address']) > 40 else r['address']
        ))
    
    print_table(headers, data, footer=f"Total drivers found: {len(data)}")
    input("\nPress Enter to continue...")