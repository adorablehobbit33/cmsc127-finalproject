import datetime

from db import execute_query, fetch_all

def violation_menu():
    while True:
        print("\n--- Violation Management ---")
        print("1. Add Violation")
        print("2. Update Violation")
        print("3. Delete Violation")
        print("4. Search Violation")
        print("5. Print All Violations")
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
        elif choice == "5":
            print_all_violations()
        elif choice == "0":
            break
        else:
            print("[!] Invalid choice.")

def add_violation():
    print("\n-- Add Violation --")
    while True:
        violation_id = input("Violation ID: ").strip()
        if len(violation_id) == 0:
            print("[!] Error: Violation ID cannot be empty.")
        elif len(violation_id) > 10:
            print(f"[!] Error: ID too long ({len(violation_id)} chars). Max allowed is 10.")
        else:
            break

    while True:
        license_number = input("Driver License Number: ").strip()
        if len(license_number) == 0:
            print("[!] Error: Driver License Number cannot be empty.")
        elif len(license_number) > 13:
            print(f"[!] Error: License too long ({len(license_number)} chars). Max allowed is 13.")
        else:
            break

    while True:
        plate_number = input("Plate Number: ").strip()
        if len(plate_number) == 0:
            print("[!] Error: Plate number cannot be empty.")
        elif len(plate_number) > 7:
            print(f"[!] Error: Plate number too long ({len(plate_number)} chars). Max allowed is 7.")
        else:
            break
    while True:
        chassis_number = input("Chassis Number: ").strip()
        if len(chassis_number) == 0:
            print("[!] Error: Chassis number cannot be empty.")
        elif len(chassis_number) > 17:
            print(f"[!] Error: Chassis number too long ({len(chassis_number)} chars). Max allowed is 17.")
        else:
            break

    while True:
        engine_number = input("Engine Number: ").strip()
        if len(engine_number) == 0:
            print("[!] Error: Engine number cannot be empty.")
        elif len(engine_number) > 17:
            print(f"[!] Error: Engine number too long ({len(engine_number)} chars). Max allowed is 17.")
        else:
            break

    while True:
        violation_date = input("Date of Violation (YYYY-MM-DD): ").strip()
        if len(violation_date) != 10 or violation_date[4] != '-' or violation_date[7] != '-':
            print("[!] Error: Invalid format. Please write exactly as YYYY-MM-DD.")
            continue
        try:
            parsed_date = datetime.strptime(violation_date, "%Y-%m-%d")
            if parsed_date > datetime.now():
                print("[!] Error: Violation incident date cannot be set in the future.")
                continue
            break
        except ValueError:
            print("[!] Error: Not a valid calendar date. Please check your parameters.")
            
    while True:
        time = input("Time (HH:MM:SS): ").strip()
        try:
            datetime.strptime(time, "%H:%M:%S")
            break
        except ValueError:
            print("[!] Error: Invalid time format. Please write exactly as HH:MM:SS.")

    while True:
        total_fine_input = input("Total Fine Amount (PHP): ").strip()
        if len(total_fine_input) == 0:
            print("[!] Error: Fine amount cannot be empty.")
            continue
        try:
            total_fine = float(total_fine_input)
            if total_fine < 0:
                print("[!] Error: Fine amount cannot be negative.")
                continue
            break
        except ValueError:
            print("[!] Error: Please enter a valid numerical decimal value.")

    while True:
        officer = input("Apprehending Officer (leave blank if none): ").strip() or "Unknown"
        if len(officer) > 50:
            print(f"[!] Error: Name too long ({len(officer)} chars). Max allowed is 50.")
        else:
            break

    allowed_statuses = ["unpaid", "paid", "contested"]
    while True:
        ticket_status = input("Ticket Status (unpaid/paid/contested): ").strip().lower()
        if ticket_status not in allowed_statuses:
            print(f"[!] Error: Choose status exactly from: {', '.join(allowed_statuses)}")
        else:
            break

    while True:
        violation_type = input("Violation Classification Type (e.g. overspeeding): ").strip()
        if len(violation_type) == 0:
            print("[!] Error: Violation classification type cannot be empty.")
        elif len(violation_type) > 50:
            print(f"[!] Error: Type too long ({len(violation_type)} chars). Max allowed by bridge is 50.")
        else:
            break
        
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
    while True:
        violation_id = input("Enter Violation ID to update: ").strip()
        if len(violation_id) == 0:
            print("[!] Error: Violation ID search field cannot be empty.")
        else:
            break

    rows = fetch_all("SELECT * FROM violation_ticket WHERE violation_id = %s", (violation_id,))
    if not rows:
        print("[!] Violation not found.")
        return

    v = rows[0]
    print(f"\nCurrent info: {v['violation_id']} | {v['ticket_status']} | Fine: {v['total_fine_amount']}")
    print("(Press Enter to keep current value)\n")

    allowed_statuses = ["unpaid", "paid", "contested"]
    while True:
        status_input = input(f"Ticket Status [{v['ticket_status']}]: ").strip().lower()
        ticket_status = status_input if status_input else v['ticket_status']
        if ticket_status not in allowed_statuses:
            print(f"[!] Error: Choose status exactly from: {', '.join(allowed_statuses)}")
        else:
            break
        
    while True:
        total_fine_input = input(f"Total Fine [{v['total_fine_amount']}]: ").strip() or v['total_fine_amount']
        if len(total_fine_input) == 0:
            print("[!] Error: Fine amount cannot be empty.")
            continue
        try:
            total_fine = float(total_fine_input)
            if total_fine < 0:
                print("[!] Error: Fine amount cannot be negative.")
                continue
            break
        except ValueError:
            print("[!] Error: Please enter a valid numerical decimal value.")

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
    while True:
        violation_id = input("Enter Violation ID to delete: ").strip()
        if len(violation_id) == 0:
            print("[!] Error: Violation ID cannot be empty.")
        else:
            break

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
    while True:
        keyword = input("Enter violation ID or driver license key to search: ").strip()
        if not keyword:
            print("[!] Error: Search criteria arguments cannot be blank spaces.")
            continue
        break
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

def print_all_violations():
    print("\n-- Incident Violation Tickets Records --")
    query = """
    SELECT vt.violation_id, 
           vt.license_number,
           CONCAT(d.first_name, ' ', d.last_name) AS driver_name,
           vtht.violation_type AS violation_name,
           vt.month, 
           vt.day, 
           vt.year,
           vt.total_fine_amount, 
           vt.ticket_status
    FROM violation_ticket vt
    JOIN driver d ON vt.license_number = d.license_number
    JOIN violation_ticket_has_type vtht ON vt.violation_id = vtht.violation_id
    ORDER BY vt.year DESC, vt.month DESC, vt.day DESC
"""
    rows = fetch_all(query)

    if not rows:
        print("[!] No violation records found.")
        return

    print(f"\n{'Violation ID':<15} {'Violation Type':<20} {'License No.':<15} {'Driver Name':<25} {'Date':<15} {'Fine':<10} {'Status':<10}")
    print("-" * 115)
    for r in rows:
        date_str = f"{r['month']} {r['day']}, {r['year']}"
        fine_str = f"PHP {r['total_fine_amount']:.2f}"
        print(f"{r['violation_id']:<15} {r['violation_name']:<20} {r['license_number']:<15} {r['driver_name']:<25} {date_str:<15} {fine_str:<10} {r['ticket_status']:<10}")