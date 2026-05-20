from colorama import Fore, Style
from db import execute_query, fetch_all
from utils.design import (
    print_header, print_success, print_error, print_info, print_warning,
    print_table, print_divider, print_subheader, input_required,
    input_option, input_date, input_license_number, input_plate_number
)

def violation_menu():
    while True:
        print_header("VIOLATION MANAGEMENT")
        print(Fore.WHITE + """
  ┌────────────────────────────────────────────────────┐
  │  1. Add Violation                                  │
  │  2. Update Violation                               │
  │  3. Delete Violation                               │
  │  4. Search Violation                               │
  │  0. Back to Main Menu                              │
  └────────────────────────────────────────────────────┘
        """)
        
        choice = input(f"{Fore.YELLOW}Enter choice:{Style.RESET_ALL} ").strip()

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
            print_error("Invalid choice.")
            input("Press Enter to continue...")

def add_violation():
    print_subheader("ADD NEW VIOLATION")
    
    violation_id = input_required("Violation ID: ", "Violation ID")
    
    # Check if violation already exists
    existing = fetch_all("SELECT violation_id FROM violation_ticket WHERE violation_id = %s", (violation_id,))
    if existing:
        print_error(f"Violation ID {violation_id} already exists!")
        input("Press Enter to continue...")
        return
    
    # Verify driver exists
    print_info("Verifying driver...")
    license_number = input_license_number()
    driver_check = fetch_all("SELECT * FROM driver WHERE license_number = %s", (license_number,))
    if not driver_check:
        print_error(f"Driver with license number {license_number} does not exist.")
        input("Press Enter to continue...")
        return
    
    # Verify vehicle exists
    print_info("Verifying vehicle...")
    plate_number = input_plate_number()
    vehicle_check = fetch_all("SELECT * FROM vehicle WHERE plate_number = %s", (plate_number,))
    if not vehicle_check:
        print_error(f"Vehicle with plate number {plate_number} does not exist.")
        input("Press Enter to continue...")
        return
    
    chassis_number = input_required("Chassis Number: ", "Chassis number") or "N/A"
    engine_number = input_required("Engine Number: ", "Engine number") or "N/A"
    
    violation_date = input_date("Date of Violation (YYYY-MM-DD): ")
    
    # Time validation
    import re
    while True:
        time = input(f"{Fore.CYAN}Time (HH:MM:SS):{Style.RESET_ALL} ").strip()
        if re.match(r'^\d{2}:\d{2}:\d{2}$', time):
            break
        print_error("Invalid time format. Please use HH:MM:SS (e.g., 14:30:00)")
    
    # Fine amount validation
    while True:
        total_fine = input(f"{Fore.CYAN}Total Fine Amount:{Style.RESET_ALL} ").strip()
        if total_fine and total_fine.replace('.', '').isdigit():
            total_fine = float(total_fine)
            break
        print_error("Please enter a valid number for fine amount")
    
    officer = input(f"{Fore.CYAN}Apprehending Officer (leave blank if none):{Style.RESET_ALL} ").strip() or "Unknown"
    ticket_status = input_option("Ticket Status:", ["unpaid", "paid", "contested"])
    
    print_info("Enter violation type (e.g., overspeeding, reckless driving, illegal parking, no seatbelt)")
    violation_type = input_required("Violation Type: ", "Violation type")

    parts = violation_date.split("-")
    year = parts[0]
    month_num = int(parts[1])
    day = parts[2]
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    month = months[month_num - 1]

    query = """
        INSERT INTO violation_ticket (violation_id, time, total_fine_amount, month, day, year,
            apprehending_officer, ticket_status, license_number, plate_number,
            chassis_number, engine_number, location)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    success, msg = execute_query(query, (
        violation_id, time, total_fine, month, day, year,
        officer, ticket_status, license_number, plate_number,
        chassis_number, engine_number, driver_check[0]['address']
    ))

    if not success:
        print_error(f"Failed to add violation ticket: {msg}")
        input("Press Enter to continue...")
        return

    query2 = """
        INSERT INTO violation_ticket_has_type (violation_id, violation_type)
        VALUES (%s, %s)
    """
    success2, msg2 = execute_query(query2, (violation_id, violation_type))

    if success2:
        driver_name = f"{driver_check[0]['first_name']} {driver_check[0]['last_name']}"
        print_success(f"Violation {violation_id} added successfully!")
        print_info(f"Driver: {driver_name} | Vehicle: {plate_number} | Fine: ₱{total_fine:,.2f}")
        print_info(f"Status: {ticket_status} | Type: {violation_type}")
    else:
        print_error(f"Ticket added but failed to set type: {msg2}")
    
    input("\nPress Enter to continue...")

def update_violation():
    print_subheader("UPDATE VIOLATION")
    violation_id = input_required("Violation ID to update: ", "Violation ID")

    rows = fetch_all("SELECT * FROM violation_ticket WHERE violation_id = %s", (violation_id,))
    if not rows:
        print_error("Violation not found.")
        input("Press Enter to continue...")
        return

    v = rows[0]
    print_info(f"Current info: ID: {v['violation_id']} | Status: {v['ticket_status']} | Fine: ₱{v['total_fine_amount']}")
    print_info("(Press Enter to keep current value)\n")

    ticket_status = input(f"{Fore.CYAN}Ticket Status [{v['ticket_status']}]:{Style.RESET_ALL} ").strip() or v['ticket_status']
    
    # Validate status
    if ticket_status not in ["unpaid", "paid", "contested"]:
        print_error("Invalid status. Must be unpaid, paid, or contested")
        input("Press Enter to continue...")
        return
    
    fine_input = input(f"{Fore.CYAN}Total Fine Amount [{v['total_fine_amount']}]:{Style.RESET_ALL} ").strip()
    if fine_input:
        if fine_input.replace('.', '').isdigit():
            total_fine = float(fine_input)
        else:
            print_error("Invalid fine amount. Keeping current value.")
            total_fine = v['total_fine_amount']
    else:
        total_fine = v['total_fine_amount']

    query = """
        UPDATE violation_ticket
        SET ticket_status = %s, total_fine_amount = %s
        WHERE violation_id = %s
    """
    success, msg = execute_query(query, (ticket_status, total_fine, violation_id))

    if success:
        print_success(f"Violation {violation_id} updated successfully!")
        print_info(f"New status: {ticket_status} | New fine: ₱{total_fine:,.2f}")
    else:
        print_error(f"Failed: {msg}")
    
    input("\nPress Enter to continue...")

def delete_violation():
    print_subheader("DELETE VIOLATION")
    violation_id = input_required("Violation ID to delete: ", "Violation ID")

    rows = fetch_all("""
        SELECT vt.*, vth.violation_type 
        FROM violation_ticket vt
        LEFT JOIN violation_ticket_has_type vth ON vt.violation_id = vth.violation_id
        WHERE vt.violation_id = %s
    """, (violation_id,))
    
    if not rows:
        print_error("Violation not found.")
        input("Press Enter to continue...")
        return

    v = rows[0]
    print_warning(f"⚠️  You are about to delete violation: {violation_id}")
    print_info(f"Driver: {v['license_number']} | Fine: ₱{v['total_fine_amount']} | Status: {v['ticket_status']}")
    if v.get('violation_type'):
        print_info(f"Type: {v['violation_type']}")
    
    confirm = input(f"{Fore.RED}Type 'DELETE' to confirm:{Style.RESET_ALL} ").strip()
    if confirm != "DELETE":
        print_warning("Cancelled.")
        input("Press Enter to continue...")
        return

    # Delete violation type first (foreign key)
    execute_query("DELETE FROM violation_ticket_has_type WHERE violation_id = %s", (violation_id,))
    success, msg = execute_query("DELETE FROM violation_ticket WHERE violation_id = %s", (violation_id,))

    if success:
        print_success(f"Violation {violation_id} deleted successfully.")
    else:
        print_error(f"Failed: {msg}")
    
    input("\nPress Enter to continue...")

def search_violation():
    print_subheader("SEARCH VIOLATION")
    print_info("Search by violation ID or license number (partial matches allowed)")
    
    keyword = input(f"{Fore.CYAN}Enter violation ID or license number to search:{Style.RESET_ALL} ").strip()
    
    if not keyword:
        print_warning("Please enter a search term")
        input("Press Enter to continue...")
        return
    
    like = f"%{keyword}%"

    query = """
        SELECT vt.violation_id, vt.license_number,
               CONCAT(d.first_name, ' ', d.last_name) AS driver_name,
               vt.month, vt.day, vt.year,
               vt.time, vt.total_fine_amount, vt.ticket_status,
               vth.violation_type, vt.apprehending_officer
        FROM violation_ticket vt
        JOIN driver d ON vt.license_number = d.license_number
        LEFT JOIN violation_ticket_has_type vth ON vt.violation_id = vth.violation_id
        WHERE vt.violation_id LIKE %s
           OR vt.license_number LIKE %s
        ORDER BY vt.year DESC, vt.month DESC, vt.day DESC
    """
    rows = fetch_all(query, (like, like))

    if not rows:
        print_warning(f"No violations found matching '{keyword}'")
        input("Press Enter to continue...")
        return

    headers = ["Violation ID", "License No", "Driver", "Date", "Time", "Fine", "Status", "Type", "Officer"]
    data = []
    for r in rows:
        date_str = f"{r['month']} {r['day']}, {r['year']}"
        data.append((
            r['violation_id'],
            r['license_number'],
            r['driver_name'][:20] if len(r['driver_name']) > 20 else r['driver_name'],
            date_str,
            r['time'],
            f"₱{r['total_fine_amount']:,.2f}",
            r['ticket_status'],
            r['violation_type'] or "N/A",
            r['apprehending_officer'][:15] if len(r['apprehending_officer']) > 15 else r['apprehending_officer']
        ))
    
    print_table(headers, data, footer=f"Total violations found: {len(data)}")
    
    # Summary statistics
    total_fines = sum(r['total_fine_amount'] for r in rows)
    paid_count = sum(1 for r in rows if r['ticket_status'] == 'paid')
    unpaid_count = sum(1 for r in rows if r['ticket_status'] == 'unpaid')
    
    print_divider()
    print_info(f"📊 Summary: Total fines: ₱{total_fines:,.2f} | Paid: {paid_count} | Unpaid: {unpaid_count}")
    
    input("\nPress Enter to continue...")