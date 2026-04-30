from db import execute_query, fetch_all

def registration_menu():
    while True:
        print("\n--- Registration Management ---")
        print("1. Add Registration")
        print("2. Update Registration")
        print("3. Delete Registration")
        print("4. Search Registration")
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
        elif choice == "0":
            break
        else:
            print("[!] Invalid choice.")

def add_registration():
    print("\n-- Add Registration --")
    registration_number = input("Registration Number: ").strip()
    registration_date = input("Registration Date (YYYY-MM-DD): ").strip()
    registration_status = input("Status (active/expired/suspended): ").strip()
    license_number = input("Driver License Number: ").strip()
    plate_number = input("Plate Number: ").strip()
    chassis_number = input("Chassis Number: ").strip()
    engine_number = input("Engine Number: ").strip()

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
    registration_number = input("Enter Registration Number to update: ").strip()

    rows = fetch_all("SELECT * FROM vehicle_registration WHERE registration_number = %s", (registration_number,))
    if not rows:
        print("[!] Registration not found.")
        return

    r = rows[0]
    print(f"\nCurrent info: {r['plate_number']} | {r['registration_status']} | {r['registration_date']}")
    print("(Press Enter to keep current value)\n")

    registration_status = input(f"Status [{r['registration_status']}]: ").strip() or r['registration_status']

    query = "UPDATE vehicle_registration SET registration_status = %s WHERE registration_number = %s"
    success, msg = execute_query(query, (registration_status, registration_number))

    if success:
        print("[✓] Registration updated successfully.")
    else:
        print(f"[✗] Failed: {msg}")

def delete_registration():
    print("\n-- Delete Registration --")
    registration_number = input("Enter Registration Number to delete: ").strip()

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