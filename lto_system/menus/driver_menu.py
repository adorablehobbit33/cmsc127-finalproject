from db import execute_query, fetch_all

def driver_menu():
    while True:
        print("\n--- Driver Management ---")
        print("1. Add Driver")
        print("2. Update Driver")
        print("3. Delete Driver")
        print("4. Search Driver")
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
        elif choice == "0":
            break
        else:
            print("[!] Invalid choice.")

def add_driver():
    print("\n-- Add Driver --")
    license_number = input("License Number (e.g. N01-23-456789): ").strip()
    first_name = input("First Name: ").strip()
    middle_name = input("Middle Name (leave blank if none): ").strip() or None
    last_name = input("Last Name: ").strip()
    date_of_birth = input("Date of Birth (YYYY-MM-DD): ").strip()
    sex = input("Sex (Male/Female): ").strip()
    address = input("Address: ").strip()
    license_type = input("License Type (Student Permit/Non-Professional/Professional): ").strip()
    license_status = input("License Status (valid/expired/suspended/revoked): ").strip()

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

def update_driver():
    print("\n-- Update Driver --")
    license_number = input("Enter License Number of driver to update: ").strip()

    rows = fetch_all("SELECT * FROM driver WHERE license_number = %s", (license_number,))
    if not rows:
        print("[!] Driver not found.")
        return

    d = rows[0]
    print(f"\nCurrent info: {d['first_name']} {d['last_name']} | {d['license_type']} | {d['license_status']}")
    print("(Press Enter to keep current value)\n")

    address = input(f"Address [{d['address']}]: ").strip() or d['address']
    license_type = input(f"License Type [{d['license_type']}]: ").strip() or d['license_type']
    license_status = input(f"License Status [{d['license_status']}]: ").strip() or d['license_status']

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
    license_number = input("Enter License Number of driver to delete: ").strip()

    rows = fetch_all("SELECT * FROM driver WHERE license_number = %s", (license_number,))
    if not rows:
        print("[!] Driver not found.")
        return

    d = rows[0]
    confirm = input(f"Delete {d['first_name']} {d['last_name']}? (yes/no): ").strip().lower()
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
               CONCAT(first_name, ' ', COALESCE(middle_name, ''), ' ', last_name) AS full_name,
               license_type, license_status, sex, date_of_birth, address
        FROM driver
        WHERE license_number LIKE %s
           OR first_name LIKE %s
           OR last_name LIKE %s
    """
    rows = fetch_all(query, (like, like, like))

    if not rows:
        print("[!] No drivers found.")
        return

    print(f"\n{'License No.':<15} {'Full Name':<30} {'Type':<20} {'Status':<12} {'Sex':<8}")
    print("-" * 90)
    for r in rows:
        print(f"{r['license_number']:<15} {r['full_name']:<30} {r['license_type']:<20} {r['license_status']:<12} {r['sex']:<8}")