from colorama import Fore, Style
from db import execute_query, fetch_all
from utils.design import (
    print_header, print_success, print_error, print_info, print_warning,
    print_table, print_divider, print_subheader, input_required,
    input_option, input_date, input_license_number, input_plate_number
)

def vehicle_menu():
    while True:
        print_header("VEHICLE MANAGEMENT")
        print(Fore.WHITE + """
  ┌────────────────────────────────────────────────────┐
  │  1. Add Vehicle                                    │
  │  2. Update Vehicle                                 │
  │  3. Delete Vehicle                                 │
  │  4. Search Vehicle                                 │
  │  0. Back to Main Menu                              │
  └────────────────────────────────────────────────────┘
        """)
        
        choice = input(f"{Fore.YELLOW}Enter choice:{Style.RESET_ALL} ").strip()

        if choice == "1":
            add_vehicle()
        elif choice == "2":
            update_vehicle()
        elif choice == "3":
            delete_vehicle()
        elif choice == "4":
            search_vehicle()
        elif choice == "0":
            break
        else:
            print_error("Invalid choice.")
            input("Press Enter to continue...")

def add_vehicle():
    print_subheader("ADD NEW VEHICLE")
    
    plate_number = input_plate_number()
    
    # Check if plate number already exists
    existing = fetch_all("SELECT plate_number FROM vehicle WHERE plate_number = %s", (plate_number,))
    if existing:
        print_error(f"Plate number {plate_number} already exists!")
        input("Press Enter to continue...")
        return
    
    chassis_number = input_required("Chassis Number: ", "Chassis number")
    engine_number = input_required("Engine Number: ", "Engine number")
    registration_number = input_required("Registration Number: ", "Registration number")
    color = input_required("Color: ", "Color")
    make = input_required("Make (e.g. Toyota, Honda, Mitsubishi): ", "Make")
    model = input_required("Model (e.g. Vios, Civic, Mirage): ", "Model")
    
    # Year validation
    while True:
        year = input(f"{Fore.CYAN}Year (e.g. 2020):{Style.RESET_ALL} ").strip()
        if year and year.isdigit() and 1900 <= int(year) <= 2025:
            break
        print_error("Please enter a valid year (1900-2025)")
    
    vehicle_type = input_option("Vehicle Type:", ["motorcycle", "private car", "public utility vehicle"])
    ownership = input_required("Ownership (e.g. Owned, Financed, Leased): ", "Ownership")
    
    # Verify owner exists
    print_info("Make sure the driver exists before adding")
    license_number = input_license_number()
    
    owner_check = fetch_all("SELECT * FROM driver WHERE license_number = %s", (license_number,))
    if not owner_check:
        print_error(f"Driver with license number {license_number} does not exist. Add driver first.")
        input("Press Enter to continue...")
        return

    query = """
        INSERT INTO vehicle (plate_number, chassis_number, engine_number, registration_number,
            color, make, model, year, vehicle_type, ownership, license_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    success, msg = execute_query(query, (
        plate_number, chassis_number, engine_number, registration_number,
        color, make, model, year, vehicle_type, ownership, license_number
    ))

    if success:
        print_success(f"Vehicle {make} {model} ({plate_number}) added successfully!")
    else:
        print_error(f"Failed: {msg}")
    
    input("\nPress Enter to continue...")

def update_vehicle():
    print_subheader("UPDATE VEHICLE")
    plate_number = input_plate_number()

    rows = fetch_all("SELECT * FROM vehicle WHERE plate_number = %s", (plate_number,))
    if not rows:
        print_error("Vehicle not found.")
        input("Press Enter to continue...")
        return

    v = rows[0]
    print_info(f"Current info: {v['make']} {v['model']} {v['year']} | {v['color']} | {v['vehicle_type']}")
    print_info("(Press Enter to keep current value)\n")

    color = input(f"{Fore.CYAN}Color [{v['color']}]:{Style.RESET_ALL} ").strip() or v['color']
    vehicle_type = input(f"{Fore.CYAN}Vehicle Type [{v['vehicle_type']}]:{Style.RESET_ALL} ").strip() or v['vehicle_type']
    ownership = input(f"{Fore.CYAN}Ownership [{v['ownership']}]:{Style.RESET_ALL} ").strip() or v['ownership']

    query = """
        UPDATE vehicle
        SET color = %s, vehicle_type = %s, ownership = %s
        WHERE plate_number = %s
    """
    success, msg = execute_query(query, (color, vehicle_type, ownership, plate_number))

    if success:
        print_success("Vehicle updated successfully.")
    else:
        print_error(f"Failed: {msg}")
    
    input("\nPress Enter to continue...")

def delete_vehicle():
    print_subheader("DELETE VEHICLE")
    plate_number = input_plate_number()

    rows = fetch_all("SELECT * FROM vehicle WHERE plate_number = %s", (plate_number,))
    if not rows:
        print_error("Vehicle not found.")
        input("Press Enter to continue...")
        return

    v = rows[0]
    print_warning(f"⚠️  You are about to delete: {v['make']} {v['model']} ({plate_number})")
    
    # Check if vehicle has violations
    violations = fetch_all("SELECT COUNT(*) as count FROM violation_ticket WHERE plate_number = %s", (plate_number,))
    if violations and violations[0]['count'] > 0:
        print_error(f"Cannot delete - vehicle has {violations[0]['count']} violation record(s).")
        input("Press Enter to continue...")
        return
    
    confirm = input(f"{Fore.RED}Type 'DELETE' to confirm:{Style.RESET_ALL} ").strip()
    if confirm != "DELETE":
        print_warning("Cancelled.")
        input("Press Enter to continue...")
        return

    success, msg = execute_query("DELETE FROM vehicle WHERE plate_number = %s", (plate_number,))
    if success:
        print_success("Vehicle deleted successfully.")
    else:
        print_error(f"Failed: {msg}")
    
    input("\nPress Enter to continue...")

def search_vehicle():
    print_subheader("SEARCH VEHICLE")
    print_info("Search by plate number, make, or model (partial matches allowed)")
    
    keyword = input(f"{Fore.CYAN}Enter plate number, make, or model to search:{Style.RESET_ALL} ").strip()
    
    if not keyword:
        print_warning("Please enter a search term")
        input("Press Enter to continue...")
        return
    
    like = f"%{keyword}%"

    query = """
        SELECT v.plate_number, v.make, v.model, v.year, v.color, v.vehicle_type,
               CONCAT(d.first_name, ' ', d.last_name) AS owner_name
        FROM vehicle v
        JOIN driver d ON v.license_number = d.license_number
        WHERE v.plate_number LIKE %s
           OR v.make LIKE %s
           OR v.model LIKE %s
        ORDER BY v.plate_number
    """
    rows = fetch_all(query, (like, like, like))

    if not rows:
        print_warning(f"No vehicles found matching '{keyword}'")
        input("Press Enter to continue...")
        return

    headers = ["Plate No", "Make", "Model", "Year", "Color", "Type", "Owner"]
    data = []
    for r in rows:
        data.append((
            r['plate_number'],
            r['make'],
            r['model'],
            r['year'],
            r['color'],
            r['vehicle_type'],
            r['owner_name']
        ))
    
    print_table(headers, data, footer=f"Total vehicles found: {len(data)}")
    input("\nPress Enter to continue...")