from datetime import datetime
from db import execute_query, fetch_all

def driver_menu():
    while True:
        print("\n--- Driver Management ---")
        print("1. Add Driver")
        print("2. Update Driver")
        print("3. Delete Driver")
        print("4. Search Driver")
        print("5. Print All Drivers")
        print("0. Back")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_driver()
        elif choice == "2":
            update_driver()
        elif choice == "3":
            delete_driver()
        elif choice == "4":
            search_driver()
        elif choice == "5":
            print_all_drivers()
        elif choice == "0":
            break
        else:
            print("[!] Invalid choice.")

def add_driver():
    print("\n-- Add Driver --")
    
    
    while True:
        license_number = input("License Number (e.g. N01-23-456789): ").strip()
        if len(license_number) == 0:
            print("[!] Error: License number cannot be empty.")
        elif len(license_number) > 13:
            print(f"[!] Error: Input too long ({len(license_number)} chars). Max allowed is 13.")
        else:
            break

    
    while True:
        first_name = input("First Name: ").strip()
        if len(first_name) == 0:
            print("[!] Error: First name cannot be empty.")
        elif len(first_name) > 50:
            print(f"[!] Error: First name too long ({len(first_name)} chars). Max allowed is 50.")
        else:
            break

    
    while True:
        middle_name = input("Middle Name (leave blank if none): ").strip() or None
        if middle_name and len(middle_name) > 50:
            print(f"[!] Error: Middle name too long ({len(middle_name)} chars). Max allowed is 50.")
        else:
            break

    # 4. Last Name Verification (Max 50 characters)
    while True:
        last_name = input("Last Name: ").strip()
        if len(last_name) == 0:
            print("[!] Error: Last name cannot be empty.")
        elif len(last_name) > 50:
            print(f"[!] Error: Last name too long ({len(last_name)} chars). Max allowed is 50.")
        else:
            break

    
    while True:
        
        date_of_birth = input("Date of Birth (YYYY-MM-DD): ").strip()
        
    
        if len(date_of_birth) != 10 or date_of_birth[4] != '-' or date_of_birth[7] != '-':
            print("[!] Error: Invalid format. Please write exactly as YYYY-MM-DD.")
            continue  # Force the loop to ask again
        try:
            dob_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
            current_date = datetime.now() # Dynamically locks to today's date
            
           
            age = current_date.year - dob_date.year
            if (current_date.month, current_date.day) < (dob_date.month, dob_date.day):
                age -= 1

           
            if dob_date >= current_date:
                print("[!] Error: Date of birth cannot be in the future.")
            elif age < 16:
                print(f"[!] Error: Driver must be at least 16 years old. (Entered age: {age})")
            else:
                break  
                
        except ValueError:
            print("[!] Error: That is not a valid date on the calendar. Check your month/day parameters.")
            continue

    
    while True:
        sex = input("Sex (Male/Female): ").strip()
        if sex not in ["Male", "Female"]:
            print("[!] Error: Please enter exactly 'Male' or 'Female'.")
        else:
            break

    
    while True:
        address = input("Address: ").strip()
        if len(address) == 0:
            print("[!] Error: Address cannot be empty.")
        elif len(address) > 255:
            print(f"[!] Error: Address too long ({len(address)} chars). Max allowed is 255.")
        else:
            break

    
    while True:
        license_type = input("License Type (Student Permit/Non-Professional/Professional): ").strip()
        if license_type not in ["Student Permit", "Non-Professional", "Professional"]:
            print("[!] Error: Invalid license type choice.")
        else:
            break

    
    while True:
        license_status = input("License Status (valid/expired/suspended/revoked): ").strip()
        if license_status not in ["valid", "expired", "suspended", "revoked"]:
            print("[!] Error: Invalid status selection.")
        else:
            break

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
        print("[✓] Driver added successfully.")
    else:
        print(f"[✗] Failed: {msg}")


#Update the driver information except for the license number and name. The user can choose to update any of the fields or keep them the same by pressing Enter.
def update_driver():
    print("\n-- Update Driver --")
    while True:
        license_number = input("License Number (e.g. N01-23-456789): ").strip()
        if len(license_number) == 0:
            print("[!] Error: License number cannot be empty.")
        elif len(license_number) > 13:
            print(f"[!] Error: Input too long ({len(license_number)} chars). Max allowed is 13.")
        else:
            break

    rows = fetch_all("SELECT * FROM driver WHERE license_number = %s", (license_number,))
    if not rows:
        print("[!] Driver not found.")
        return

    driver = rows[0]
    print(f"\nCurrent info: {driver['first_name']} {driver['last_name']} | {driver['license_type']} | {driver['license_status']}")
    print("(Press Enter to keep current value)\n")

   
    while True:
        address_input = input(f"Address [{driver['address']}]: ").strip()
        address = address_input if address_input else driver['address']
        
        if len(address) > 255:
            print(f"[!] Error: Address too long ({len(address)} chars). Max allowed is 255.")
        elif len(address) == 0:
            print("[!] Error: Address cannot be empty.")
        else:
            break

   
    allowed_types = ["Student Permit", "Non-Professional", "Professional"]
    while True:
        type_input = input(f"License Type [{driver['license_type']}]: ").strip()
        license_type = type_input if type_input else driver['license_type']
        
        if license_type not in allowed_types:
            print(f"[!] Error: Invalid type. Must be one of: {', '.join(allowed_types)}")
        else:
            break

    
    allowed_statuses = ["valid", "expired", "suspended", "revoked"]
    while True:
        status_input = input(f"License Status [{driver['license_status']}]: ").strip()
        license_status = status_input if status_input else driver['license_status']
        
        if license_status not in allowed_statuses:
            print(f"[!] Error: Invalid status. Must be one of: {', '.join(allowed_statuses)}")
        else:
            break

    query = """
        UPDATE driver
        SET address = %s, license_type = %s, license_status = %s
        WHERE license_number = %s
    """
    success, msg = execute_query(query, (address, license_type, license_status, license_number))

    if success:
        print("[✓] Driver updated successfully.")
    else:
        print(f"[✗] Failed: {msg}")

def delete_driver():
    print("\n-- Delete Driver --")
    while True:
        license_number = input("License Number (e.g. N01-23-456789): ").strip()
        if len(license_number) == 0:
            print("[!] Error: License number cannot be empty.")
        elif len(license_number) > 13:
            print(f"[!] Error: Input too long ({len(license_number)} chars). Max allowed is 13.")
        else:
            break

    rows = fetch_all("SELECT * FROM driver WHERE license_number = %s", (license_number,))
    if not rows:
        print("[!] Driver not found.")
        return

    driver = rows[0]
    confirm = input(f"Delete {driver['first_name']} {driver['last_name']}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("[!] Cancelled.")
        return

    success, msg = execute_query("DELETE FROM driver WHERE license_number = %s", (license_number,))
    if success:
        print("[✓] Driver deleted successfully.")
    else:
        print(f"[✗] Failed: {msg}")

def search_driver():
    print("\n-- Search Driver --")
    keyword = input("Enter name or license number to search: ").strip()
    like = f"%{keyword}%"

    query = """
        SELECT license_number,
               TRIM(REPLACE(CONCAT(first_name, ' ', COALESCE(middle_name, ''), ' ', last_name), '  ', ' ')) AS full_name,
               license_type, license_status, sex, date_of_birth, address
        FROM driver
        WHERE license_number LIKE %s
           OR first_name LIKE %s
           OR last_name LIKE %s
           OR TRIM(REPLACE(CONCAT(first_name, ' ', last_name), '  ', ' ')) LIKE %s
           OR TRIM(REPLACE(CONCAT(first_name, ' ', COALESCE(middle_name, ''), ' ', last_name), '  ', ' ')) LIKE %s
    """
    rows = fetch_all(query, (like, like, like, like, like))

    if not rows:
        print("[!] No drivers found.")
        return

    print(f"\n{'License No.':<15} {'Full Name':<30} {'Type':<20} {'Status':<12} {'Sex':<8}")
    print("-" * 90)
    for r in rows:
        print(f"{r['license_number']:<15} {r['full_name']:<30} {r['license_type']:<20} {r['license_status']:<12} {r['sex']:<8}")

def print_all_drivers():
    print("\n-- All Drivers Registry --")
    query = """
        SELECT license_number,
               CONCAT(first_name, ' ', COALESCE(middle_name, ''), ' ', last_name) AS full_name,
               license_type, license_status, sex, date_of_birth, address
        FROM driver
        ORDER BY last_name, first_name
    """
    rows = fetch_all(query)

    if not rows:
        print("[!] No drivers registered in the system.")
        return

    print(f"\n{'License No.':<15} {'Full Name':<25} {'Type':<18} {'Status':<10} {'Sex':<8} {'DOB':<12}")
    print("-" * 90)
    for r in rows:
        name = " ".join(r['full_name'].split())
        print(f"{r['license_number']:<15} {name:<25} {r['license_type']:<18} {r['license_status']:<10} {r['sex']:<8} {str(r['date_of_birth']):<12}")