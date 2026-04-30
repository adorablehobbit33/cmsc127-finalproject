from db import execute_query, fetch_all

def violation_menu():
    while True:
        print("\n--- Violation Management ---")
        print("1. Add Violation")
        print("2. Update Violation")
        print("3. Delete Violation")
        print("4. Search Violation")
        print("0. Back")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_violation()
        elif choice == "2":
            update_violation()
        elif choice == "3":
            delete_violation()
        elif choice == "4":
            search_violation()
        elif choice == "0":
            break
        else:
            print("[!] Invalid choice.")

def add_violation():
    print("\n-- Add Violation --")
    violation_id = input("Violation ID: ").strip()
    license_number = input("Driver License Number: ").strip()
    plate_number = input("Plate Number: ").strip()
    chassis_number = input("Chassis Number: ").strip()
    engine_number = input("Engine Number: ").strip()
    violation_date = input("Date of Violation (YYYY-MM-DD): ").strip()
    time = input("Time (HH:MM:SS): ").strip()
    total_fine = input("Total Fine Amount: ").strip()
    officer = input("Apprehending Officer (leave blank if none): ").strip() or "Unknown"
    ticket_status = input("Ticket Status (unpaid/paid/contested): ").strip()
    violation_type = input("Violation Type (e.g. overspeeding, reckless driving): ").strip()

    parts = violation_date.split("-")
    year = parts[0]
    month_num = int(parts[1])
    day = parts[2]
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    month = months[month_num - 1]

    query = """
        INSERT INTO violation_ticket (violation_id, time, total_fine_amount, month, day, year,
            apprehending_officer, ticket_status, license_number, plate_number,
            chassis_number, engine_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    success, msg = execute_query(query, (
        violation_id, time, total_fine, month, day, year,
        officer, ticket_status, license_number, plate_number,
        chassis_number, engine_number
    ))

    if not success:
        print(f"[✗] Failed to add violation ticket: {msg}")
        return

    query2 = """
        INSERT INTO violation_ticket_has_type (violation_id, violation_type)
        VALUES (%s, %s)
    """
    success2, msg2 = execute_query(query2, (violation_id, violation_type))

    if success2:
        print("[✓] Violation added successfully.")
    else:
        print(f"[✗] Ticket added but failed to set type: {msg2}")

def update_violation():
    print("\n-- Update Violation --")
    violation_id = input("Enter Violation ID to update: ").strip()

    rows = fetch_all("SELECT * FROM violation_ticket WHERE violation_id = %s", (violation_id,))
    if not rows:
        print("[!] Violation not found.")
        return

    v = rows[0]
    print(f"\nCurrent info: {v['violation_id']} | {v['ticket_status']} | Fine: {v['total_fine_amount']}")
    print("(Press Enter to keep current value)\n")

    ticket_status = input(f"Ticket Status [{v['ticket_status']}]: ").strip() or v['ticket_status']
    total_fine = input(f"Total Fine [{v['total_fine_amount']}]: ").strip() or v['total_fine_amount']

    query = """
        UPDATE violation_ticket
        SET ticket_status = %s, total_fine_amount = %s
        WHERE violation_id = %s
    """
    success, msg = execute_query(query, (ticket_status, total_fine, violation_id))

    if success:
        print("[✓] Violation updated successfully.")
    else:
        print(f"[✗] Failed: {msg}")

def delete_violation():
    print("\n-- Delete Violation --")
    violation_id = input("Enter Violation ID to delete: ").strip()

    rows = fetch_all("SELECT * FROM violation_ticket WHERE violation_id = %s", (violation_id,))
    if not rows:
        print("[!] Violation not found.")
        return

    confirm = input(f"Delete violation {violation_id}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("[!] Cancelled.")
        return

    execute_query("DELETE FROM violation_ticket_has_type WHERE violation_id = %s", (violation_id,))
    success, msg = execute_query("DELETE FROM violation_ticket WHERE violation_id = %s", (violation_id,))

    if success:
        print("[✓] Violation deleted successfully.")
    else:
        print(f"[✗] Failed: {msg}")

def search_violation():
    print("\n-- Search Violation --")
    keyword = input("Enter violation ID or license number to search: ").strip()
    like = f"%{keyword}%"

    query = """
        SELECT vt.violation_id, vt.license_number,
               CONCAT(d.first_name, ' ', d.last_name) AS driver_name,
               vt.month, vt.day, vt.year,
               vt.total_fine_amount, vt.ticket_status
        FROM violation_ticket vt
        JOIN driver d ON vt.license_number = d.license_number
        WHERE vt.violation_id LIKE %s
           OR vt.license_number LIKE %s
    """
    rows = fetch_all(query, (like, like))

    if not rows:
        print("[!] No violations found.")
        return

    print(f"\n{'Violation ID':<15} {'License No.':<15} {'Driver':<25} {'Date':<20} {'Fine':<10} {'Status':<12}")
    print("-" * 100)
    for r in rows:
        date = f"{r['month']} {r['day']}, {r['year']}"
        print(f"{r['violation_id']:<15} {r['license_number']:<15} {r['driver_name']:<25} {date:<20} {str(r['total_fine_amount']):<10} {r['ticket_status']:<12}")