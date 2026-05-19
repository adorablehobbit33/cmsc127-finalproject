from datetime import datetime

from db import execute_query, fetch_all

def registration_menu():
    while True:
        print("\n--- Registration Management ---")
        print("1. Add Registration")
        print("2. Update Registration")
        print("3. Delete Registration")
        print("4. Search Registration")
        print("5. Print All Registrations")
        print("0. Back")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_registration()
        elif choice == "2":
            update_registration()
        elif choice == "3":
            delete_registration()
        elif choice == "4":
            search_registration()
        elif choice == "5":
            print_all_registrations()
        elif choice == "0":
            break
        else:
            print("[!] Invalid choice.")

def add_registration():
    print("\n-- Add Registration --")
    while True:
        registration_number = input("Registration Number: ").strip()
        if len(registration_number) == 0:
            print("[!] Error: Registration number cannot be empty.")
        elif len(registration_number) > 7:
            print(f"[!] Error: Input too long ({len(registration_number)} chars). Max allowed is 7.")
        else:
            break

        
    while True:
        registration_date = input("Registration Date (YYYY-MM-DD): ").strip()
        
        if len(registration_date) != 10 or registration_date[4] != '-' or registration_date[7] != '-':
            print("[!] Error: Invalid format. Please write exactly as YYYY-MM-DD.")
            continue

        try:
            # Safely parse string into a true datetime object to evaluate calendars
            parsed_date = datetime.strptime(registration_date, "%Y-%m-%d")
            current_date = datetime.now()
            
            # Close edge case: Reject future dates
            if parsed_date > current_date:
                print("[!] Error: Registration date cannot be in the future.")
                continue

            break
            
        except ValueError:
            print("[!] Error: That is not a valid date on the calendar. Check your month/day parameters.")
            continue

    allowed_statuses = ["active", "expired", "suspended"]
    while True:
        registration_status = input("Status (active/expired/suspended): ").strip().lower()
        if len(registration_status) > 20:
            print("[!] Error: Input status length cannot exceed 20 characters.")
        elif registration_status not in allowed_statuses:
            print(f"[!] Error: Invalid choice. Choose exactly from: {', '.join(allowed_statuses)}")
        else:
            break

    while True:
        license_number = input("License Number (e.g. N01-23-456789): ").strip()
        if len(license_number) == 0:
            print("[!] Error: License number cannot be empty.")
        elif len(license_number) > 13:
            print(f"[!] Error: Input too long ({len(license_number)} chars). Max allowed is 13.")
        else:
            break

    while True:
        plate_number = input("Plate Number: ").strip()
        if len(plate_number) == 0:
            print("[!] Error: Plate number cannot be empty.")
        if plate_number and len(plate_number) > 7:
            print(f"[!] Error: Input too long ({len(plate_number)} chars). Max allowed is 7.")
        else:
            break


    while True:
        chassis_number = input("Chassis Number: ").strip()
        if len(chassis_number) == 0:
            print("[!] Error: Chassis number cannot be empty.")
        elif len(chassis_number) > 17:
            print(f"[!] Error: Input too long ({len(chassis_number)} chars). Max allowed is 17.")
        else:
            break

    while True:
        engine_number = input("Engine Number: ").strip()
        if len(engine_number) == 0:
            print("[!] Error: Engine number cannot be empty.")
        elif len(engine_number) > 17:
            print(f"[!] Error: Input too long ({len(engine_number)} chars). Max allowed is 17.")
        else:
            break

    # Parse date parts from registration_date
    parts = registration_date.split("-")
    year = parts[0]
    month_num = int(parts[1])
    day = parts[2]
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    month = months[month_num - 1]

    query = """
        INSERT INTO vehicle_registration (registration_number, registration_date,
            registration_status, month, day, year, license_number, plate_number,
            chassis_number, engine_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    success, msg = execute_query(query, (
        registration_number, registration_date, registration_status,
        month, day, year, license_number, plate_number, chassis_number, engine_number
    ))

    if success:
        print("[✓] Registration added successfully.")
    else:
        print(f"[✗] Failed: {msg}")

def update_registration():
    print("\n-- Update Registration --")
    while True:
        registration_number = input("Enter Registration Number to update: ").strip()
        if len(registration_number) == 0:
            print("[!] Error: Registration number cannot be empty.")
        elif len(registration_number) > 7:
            print(f"[!] Error: Input too long ({len(registration_number)} chars). Max allowed is 7.")
        else:
            break

    rows = fetch_all("SELECT * FROM vehicle_registration WHERE registration_number = %s", (registration_number,))
    if not rows:
        print("[!] Registration not found.")
        return

    r = rows[0]
    print(f"\nCurrent info: {r['plate_number']} | {r['registration_status']} | {r['registration_date']}")
    print("(Press Enter to keep current value)\n")


    while True:
        registration_input = input(f"Status [{r['registration_status']}]: ").strip() 
        registration_status = registration_input if registration_input else r['registration_status']

        if registration_status and len(registration_status) > 20:
            print("[!] Error: Input status length cannot exceed 20 characters.")
        elif registration_status and registration_status.lower() not in ["active", "expired", "suspended"]:
            print(f"[!] Error: Invalid choice. Choose exactly from: active, expired, suspended")
        else:
            break

    query = "UPDATE vehicle_registration SET registration_status = %s WHERE registration_number = %s"
    success, msg = execute_query(query, (registration_status, registration_number))

    if success:
        print("[✓] Registration updated successfully.")
    else:
        print(f"[✗] Failed: {msg}")

def delete_registration():
    print("\n-- Delete Registration --")
    while True:
        registration_number = input("Enter Registration Number to delete: ").strip()
        if len(registration_number) == 0:
            print("[!] Error: Registration number cannot be empty.")
        elif len(registration_number) > 7:
            print(f"[!] Error: Input too long ({len(registration_number)} chars). Max allowed is 7.")
        else:
            break
    rows = fetch_all("SELECT * FROM vehicle_registration WHERE registration_number = %s", (registration_number,))
    if not rows:
        print("[!] Registration not found.")
        return

    r = rows[0]
    confirm = input(f"Delete registration {r['registration_number']} for plate {r['plate_number']}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("[!] Cancelled.")
        return

    success, msg = execute_query("DELETE FROM vehicle_registration WHERE registration_number = %s", (registration_number,))
    if success:
        print("[✓] Registration deleted successfully.")
    else:
        print(f"[✗] Failed: {msg}")

def search_registration():
    print("\n-- Search Registration --")
    keyword = input("Enter registration number or plate number to search: ").strip()
    like = f"%{keyword}%"

    query = """
        SELECT vr.registration_number, vr.plate_number, vr.registration_date,
               vr.registration_status,
               DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) AS expiration_date
        FROM vehicle_registration vr
        WHERE vr.registration_number LIKE %s
           OR vr.plate_number LIKE %s
    """
    rows = fetch_all(query, (like, like))

    if not rows:
        print("[!] No registrations found.")
        return

    print(f"\n{'Reg No.':<10} {'Plate No.':<12} {'Reg Date':<14} {'Expiry Date':<14} {'Status':<12}")
    print("-" * 65)
    for r in rows:
        print(f"{r['registration_number']:<10} {r['plate_number']:<12} {str(r['registration_date']):<14} {str(r['expiration_date']):<14} {r['registration_status']:<12}")

def print_all_registrations():
    print("\n-- All Vehicle Registrations Ledger --")
    query = """
        SELECT vr.registration_number, vr.plate_number, vr.registration_date,
               vr.registration_status,
               DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) AS expiration_date
        FROM vehicle_registration vr
        ORDER BY vr.registration_date DESC
    """
    rows = fetch_all(query)

    if not rows:
        print("[!] No registrations found in the system.")
        return

    print(f"\n{'Reg No.':<12} {'Plate No.':<12} {'Reg Date':<14} {'Expiry Date':<14} {'Status':<10}")
    print("-" * 80)
    for r in rows:
        print(f"{r['registration_number']:<12} {r['plate_number']:<12} {str(r['registration_date']):<14} {str(r['expiration_date']):<14} {r['registration_status']:<10}")