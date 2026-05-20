from colorama import Fore, Style
from db import execute_query, fetch_all
from utils.design import (
    print_header, print_success, print_error, print_info, print_warning,
    print_table, print_divider, print_subheader, input_required,
    input_option, input_date, input_license_number, input_plate_number
)

def registration_menu():
    while True:
        print_header("REGISTRATION MANAGEMENT")
        print(Fore.WHITE + """
  ┌────────────────────────────────────────────────────┐
  │  1. Add Registration                               │
  │  2. Update Registration                            │
  │  3. Delete Registration                            │
  │  4. Search Registration                            │
  │  0. Back to Main Menu                              │
  └────────────────────────────────────────────────────┘
        """)
        
        choice = input(f"{Fore.YELLOW}Enter choice:{Style.RESET_ALL} ").strip()

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
            print_error("Invalid choice.")
            input("Press Enter to continue...")

def add_registration():
    print_subheader("ADD NEW REGISTRATION")
    
    registration_number = input_required("Registration Number: ", "Registration number")
    
    # Check if registration already exists
    existing = fetch_all("SELECT registration_number FROM vehicle_registration WHERE registration_number = %s", (registration_number,))
    if existing:
        print_error(f"Registration number {registration_number} already exists!")
        input("Press Enter to continue...")
        return
    
    registration_date = input_date("Registration Date (YYYY-MM-DD): ")
    
    # Parse date parts from registration_date
    parts = registration_date.split("-")
    year = parts[0]
    month_num = int(parts[1])
    day = parts[2]
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    month = months[month_num - 1]
    
    # Calculate expiration date for display
    from datetime import datetime, timedelta
    reg_date_obj = datetime.strptime(registration_date, "%Y-%m-%d")
    exp_date = reg_date_obj + timedelta(days=365)
    print_info(f"Expiration date will be: {exp_date.strftime('%Y-%m-%d')}")
    
    registration_status = input_option("Registration Status:", ["active", "expired", "suspended"])
    
    # Verify driver exists
    print_info("Verifying driver...")
    license_number = input_license_number()
    driver_check = fetch_all("SELECT * FROM driver WHERE license_number = %s", (license_number,))
    if not driver_check:
        print_error(f"Driver with license number {license_number} does not exist. Add driver first.")
        input("Press Enter to continue...")
        return
    
    # Verify vehicle exists
    print_info("Verifying vehicle...")
    plate_number = input_plate_number()
    vehicle_check = fetch_all("SELECT * FROM vehicle WHERE plate_number = %s", (plate_number,))
    if not vehicle_check:
        print_error(f"Vehicle with plate number {plate_number} does not exist. Add vehicle first.")
        input("Press Enter to continue...")
        return
    
    chassis_number = input_required("Chassis Number: ", "Chassis number")
    engine_number = input_required("Engine Number: ", "Engine number")

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
        print_success(f"Registration {registration_number} added successfully!")
        print_info(f"Vehicle {plate_number} registered to {driver_check[0]['first_name']} {driver_check[0]['last_name']}")
    else:
        print_error(f"Failed: {msg}")
    
    input("\nPress Enter to continue...")

def update_registration():
    print_subheader("UPDATE REGISTRATION")
    registration_number = input_required("Registration Number to update: ", "Registration number")

    rows = fetch_all("SELECT * FROM vehicle_registration WHERE registration_number = %s", (registration_number,))
    if not rows:
        print_error("Registration not found.")
        input("Press Enter to continue...")
        return

    r = rows[0]
    print_info(f"Current info: Plate: {r['plate_number']} | Status: {r['registration_status']} | Date: {r['registration_date']}")
    print_info("(Press Enter to keep current value)\n")

    registration_status = input(f"{Fore.CYAN}Status [{r['registration_status']}]:{Style.RESET_ALL} ").strip() or r['registration_status']
    
    # Validate status
    if registration_status not in ["active", "expired", "suspended"]:
        print_error("Invalid status. Must be active, expired, or suspended")
        input("Press Enter to continue...")
        return

    query = "UPDATE vehicle_registration SET registration_status = %s WHERE registration_number = %s"
    success, msg = execute_query(query, (registration_status, registration_number))

    if success:
        print_success(f"Registration {registration_number} updated to '{registration_status}'")
    else:
        print_error(f"Failed: {msg}")
    
    input("\nPress Enter to continue...")

def delete_registration():
    print_subheader("DELETE REGISTRATION")
    registration_number = input_required("Registration Number to delete: ", "Registration number")

    rows = fetch_all("SELECT * FROM vehicle_registration WHERE registration_number = %s", (registration_number,))
    if not rows:
        print_error("Registration not found.")
        input("Press Enter to continue...")
        return

    r = rows[0]
    print_warning(f"⚠️  You are about to delete registration for plate: {r['plate_number']}")
    print_info(f"Registration date: {r['registration_date']}")
    
    confirm = input(f"{Fore.RED}Type 'DELETE' to confirm:{Style.RESET_ALL} ").strip()
    if confirm != "DELETE":
        print_warning("Cancelled.")
        input("Press Enter to continue...")
        return

    success, msg = execute_query("DELETE FROM vehicle_registration WHERE registration_number = %s", (registration_number,))
    if success:
        print_success("Registration deleted successfully.")
    else:
        print_error(f"Failed: {msg}")
    
    input("\nPress Enter to continue...")

def search_registration():
    print_subheader("SEARCH REGISTRATION")
    print_info("Search by registration number or plate number (partial matches allowed)")
    
    keyword = input(f"{Fore.CYAN}Enter registration number or plate number to search:{Style.RESET_ALL} ").strip()
    
    if not keyword:
        print_warning("Please enter a search term")
        input("Press Enter to continue...")
        return
    
    like = f"%{keyword}%"

    query = """
        SELECT vr.registration_number, vr.plate_number, vr.registration_date,
               vr.registration_status,
               DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) AS expiration_date,
               CONCAT(d.first_name, ' ', d.last_name) AS owner_name
        FROM vehicle_registration vr
        JOIN driver d ON vr.license_number = d.license_number
        WHERE vr.registration_number LIKE %s
           OR vr.plate_number LIKE %s
        ORDER BY vr.registration_date DESC
    """
    rows = fetch_all(query, (like, like))

    if not rows:
        print_warning(f"No registrations found matching '{keyword}'")
        input("Press Enter to continue...")
        return

    headers = ["Reg No", "Plate No", "Reg Date", "Expiry Date", "Status", "Owner"]
    data = []
    for r in rows:
        data.append((
            r['registration_number'],
            r['plate_number'],
            r['registration_date'],
            r['expiration_date'],
            r['registration_status'],
            r['owner_name']
        ))
    
    print_table(headers, data, footer=f"Total registrations found: {len(data)}")
    
    # Show upcoming expirations warning
    from datetime import datetime
    today = datetime.now().date()
    expiring_soon = []
    for r in rows:
        if r['expiration_date'] and r['expiration_date'] <= today:
            expiring_soon.append(r['plate_number'])
    
    if expiring_soon:
        print_warning(f"⚠️  Expired registrations for: {', '.join(expiring_soon)}")
    
    input("\nPress Enter to continue...")