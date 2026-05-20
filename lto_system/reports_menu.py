from colorama import Fore, Style
from db import fetch_all
from utils.design import (
    print_header, print_success, print_error, print_info, print_warning,
    print_table, print_divider, print_subheader, input_required,
    input_option, input_date, input_license_number, input_plate_number
)

def reports_menu():
    while True:
        print_header("REPORTS")
        print(Fore.WHITE + """
  ┌────────────────────────────────────────────────────────────────────┐
  │  1. Drivers filtered by license type, status, age range, sex      │
  │  2. Vehicles owned by a driver                                    │
  │  3. Vehicles with expired registrations as of a given date        │
  │  4. Drivers with expired or suspended licenses                    │
  │  5. Violations by a driver within a date range                    │
  │  6. Total violations per type for a given year                    │
  │  7. Vehicles involved in violations within a city or region       │
  │  0. Back to Main Menu                                             │
  └────────────────────────────────────────────────────────────────────┘
        """)
        
        choice = input(f"{Fore.YELLOW}Enter choice:{Style.RESET_ALL} ").strip()

        if choice == "1":
            report_drivers_filtered()
        elif choice == "2":
            report_vehicles_by_driver()
        elif choice == "3":
            report_expired_registrations()
        elif choice == "4":
            report_invalid_licenses()
        elif choice == "5":
            report_violations_by_driver()
        elif choice == "6":
            report_violations_per_type()
        elif choice == "7":
            report_vehicles_by_location()
        elif choice == "0":
            break
        else:
            print_error("Invalid choice.")
            input("Press Enter to continue...")


# ── Report 1 ──────────────────────────────────────────────────────────────────
def report_drivers_filtered():
    print_subheader("REPORT 1: Filtered Drivers")
    print_info("(Press Enter to skip any filter)\n")

    license_type   = input(f"{Fore.CYAN}License Type (Student Permit / Non-Professional / Professional):{Style.RESET_ALL} ").strip()
    license_status = input(f"{Fore.CYAN}License Status (valid / expired / suspended / revoked):{Style.RESET_ALL} ").strip()
    sex            = input(f"{Fore.CYAN}Sex (Male / Female):{Style.RESET_ALL} ").strip()
    age_min        = input(f"{Fore.CYAN}Minimum Age:{Style.RESET_ALL} ").strip()
    age_max        = input(f"{Fore.CYAN}Maximum Age:{Style.RESET_ALL} ").strip()

    age_calc = "(YEAR(CURDATE()) - YEAR(date_of_birth) - (DATE_FORMAT(CURDATE(),'%m%d') < DATE_FORMAT(date_of_birth,'%m%d')))"
    
    query = f"""
        SELECT
            license_number,
            CONCAT(first_name, ' ', COALESCE(middle_name, ''), ' ', last_name) AS full_name,
            date_of_birth,
            sex,
            address,
            license_type,
            license_status,
            {age_calc} AS age
        FROM driver
        WHERE 1=1
    """
    params = []

    if license_type:
        query += " AND license_type = %s"
        params.append(license_type)
    if license_status:
        query += " AND license_status = %s"
        params.append(license_status)
    if sex:
        query += " AND sex = %s"
        params.append(sex)
    if age_min:
        query += f" AND {age_calc} >= %s"
        params.append(int(age_min))
    if age_max:
        query += f" AND {age_calc} <= %s"
        params.append(int(age_max))

    query += " ORDER BY license_number"
    
    rows = fetch_all(query, params)
    
    if not rows:
        print_warning("No drivers found matching the criteria.")
        input("\nPress Enter to continue...")
        return

    headers = ["License No", "Full Name", "Type", "Status", "Sex", "Age", "Address"]
    data = []
    for r in rows:
        data.append((
            r['license_number'],
            r['full_name'][:28] if len(r['full_name']) > 28 else r['full_name'],
            r['license_type'],
            r['license_status'],
            r['sex'],
            r['age'],
            r['address'][:35] + "..." if len(r['address']) > 35 else r['address']
        ))
    
    print_table(headers, data, footer=f"Total drivers found: {len(data)}")
    input("\nPress Enter to continue...")


# ── Report 2 ──────────────────────────────────────────────────────────────────
def report_vehicles_by_driver():
    print_subheader("REPORT 2: Vehicles Owned by a Driver")
    
    license_number = input_license_number()

    # Get driver name first
    driver = fetch_all("SELECT CONCAT(first_name, ' ', last_name) AS name FROM driver WHERE license_number = %s", (license_number,))
    if driver:
        print_info(f"Showing vehicles for: {driver[0]['name']}")
    else:
        print_error(f"Driver with license number {license_number} not found.")
        input("\nPress Enter to continue...")
        return

    query = """
        SELECT
            v.plate_number, v.make, v.model, v.year,
            v.color, v.vehicle_type, v.chassis_number, v.engine_number
        FROM vehicle v
        WHERE v.license_number = %s
        ORDER BY v.plate_number
    """
    rows = fetch_all(query, (license_number,))
    
    if not rows:
        print_warning("No vehicles found for that driver.")
        input("\nPress Enter to continue...")
        return

    headers = ["Plate No", "Make", "Model", "Year", "Color", "Type", "Chassis", "Engine"]
    data = []
    for r in rows:
        data.append((
            r['plate_number'],
            r['make'],
            r['model'],
            r['year'],
            r['color'],
            r['vehicle_type'],
            r['chassis_number'][:10] + "..." if len(r['chassis_number']) > 10 else r['chassis_number'],
            r['engine_number'][:10] + "..." if len(r['engine_number']) > 10 else r['engine_number']
        ))
    
    print_table(headers, data, footer=f"Total vehicles owned: {len(data)}")
    input("\nPress Enter to continue...")


# ── Report 3 ──────────────────────────────────────────────────────────────────
def report_expired_registrations():
    print_subheader("REPORT 3: Vehicles with Expired Registrations")
    
    as_of_date = input(f"{Fore.CYAN}As of date (YYYY-MM-DD, press Enter for today):{Style.RESET_ALL} ").strip()
    
    from datetime import datetime
    if not as_of_date:
        as_of_date = datetime.now().strftime("%Y-%m-%d")
        print_info(f"Using today's date: {as_of_date}")

    query = """
        SELECT
            vr.registration_number,
            vr.plate_number,
            v.make, v.model, v.year,
            vr.registration_date,
            DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) AS expiration_date,
            vr.registration_status,
            CONCAT(d.first_name, ' ', d.last_name) AS owner_name
        FROM vehicle_registration vr
        JOIN vehicle v ON vr.plate_number = v.plate_number
        JOIN driver  d ON vr.license_number = d.license_number
        WHERE DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) < %s
           OR vr.registration_status = 'expired'
        ORDER BY expiration_date
    """
    rows = fetch_all(query, (as_of_date,))
    
    if not rows:
        print_success(f"No expired registrations found as of {as_of_date}.")
        input("\nPress Enter to continue...")
        return

    headers = ["Reg No", "Plate No", "Make/Model", "Reg Date", "Expiry Date", "Status", "Owner"]
    data = []
    for r in rows:
        make_model = f"{r['make']} {r['model']}"
        status_color = Fore.RED if r['registration_status'] == 'expired' else Fore.YELLOW
        data.append((
            r['registration_number'],
            r['plate_number'],
            make_model[:18] if len(make_model) > 18 else make_model,
            r['registration_date'],
            r['expiration_date'],
            f"{status_color}{r['registration_status']}{Style.RESET_ALL}",
            r['owner_name'][:20] if len(r['owner_name']) > 20 else r['owner_name']
        ))
    
    print_table(headers, data, footer=f"Total expired registrations found: {len(data)}")
    input("\nPress Enter to continue...")


# ── Report 4 ──────────────────────────────────────────────────────────────────
def report_invalid_licenses():
    print_subheader("REPORT 4: Drivers with Expired or Suspended Licenses")

    query = """
        SELECT
            license_number,
            CONCAT(first_name, ' ', COALESCE(middle_name, ''), ' ', last_name) AS driver_name,
            license_type, license_status, date_of_birth, address
        FROM driver
        WHERE license_status IN ('expired', 'suspended')
        ORDER BY license_status, last_name
    """
    rows = fetch_all(query)
    
    if not rows:
        print_success("No drivers with expired or suspended licenses found.")
        input("\nPress Enter to continue...")
        return

    headers = ["License No", "Driver Name", "Type", "Status", "DOB", "Address"]
    data = []
    for r in rows:
        status_color = Fore.RED if r['license_status'] == 'expired' else Fore.YELLOW
        data.append((
            r['license_number'],
            r['driver_name'][:25] if len(r['driver_name']) > 25 else r['driver_name'],
            r['license_type'],
            f"{status_color}{r['license_status']}{Style.RESET_ALL}",
            r['date_of_birth'],
            r['address'][:30] + "..." if len(r['address']) > 30 else r['address']
        ))
    
    expired_count = sum(1 for r in rows if r['license_status'] == 'expired')
    suspended_count = sum(1 for r in rows if r['license_status'] == 'suspended')
    
    print_table(headers, data, footer=f"Expired: {expired_count} | Suspended: {suspended_count} | Total: {len(rows)}")
    input("\nPress Enter to continue...")


# ── Report 5 ──────────────────────────────────────────────────────────────────
def report_violations_by_driver():
    print_subheader("REPORT 5: Violations by Driver within Date Range")
    
    license_number = input_license_number()
    
    # Get driver name
    driver = fetch_all("SELECT CONCAT(first_name, ' ', last_name) AS name FROM driver WHERE license_number = %s", (license_number,))
    if driver:
        print_info(f"Showing violations for: {driver[0]['name']}")
    else:
        print_error(f"Driver with license number {license_number} not found.")
        input("\nPress Enter to continue...")
        return
    
    date_from = input_date("From date (YYYY-MM-DD): ")
    date_to = input_date("To date (YYYY-MM-DD): ")

    query = """
        SELECT
            vt.violation_id,
            vt.ticket_status,
            vt.total_fine_amount,
            vt.apprehending_officer,
            vt.plate_number,
            STR_TO_DATE(CONCAT(vt.year,'-',vt.month,'-',vt.day), '%Y-%M-%d') AS violation_date,
            GROUP_CONCAT(vtht.violation_type SEPARATOR ', ') AS violation_types
        FROM violation_ticket vt
        LEFT JOIN violation_ticket_has_type vtht ON vt.violation_id = vtht.violation_id
        WHERE vt.license_number = %s
          AND STR_TO_DATE(CONCAT(vt.year,'-',vt.month,'-',vt.day), '%Y-%M-%d')
              BETWEEN %s AND %s
        GROUP BY vt.violation_id
        ORDER BY violation_date
    """
    rows = fetch_all(query, (license_number, date_from, date_to))
    
    if not rows:
        print_warning(f"No violations found for this driver between {date_from} and {date_to}.")
        input("\nPress Enter to continue...")
        return

    headers = ["Violation ID", "Date", "Plate No", "Type(s)", "Fine", "Status", "Officer"]
    data = []
    total_fines = 0
    for r in rows:
        total_fines += r['total_fine_amount']
        status_color = ""
        if r['ticket_status'] == 'paid':
            status_color = Fore.GREEN
        elif r['ticket_status'] == 'unpaid':
            status_color = Fore.RED
        else:
            status_color = Fore.YELLOW
            
        data.append((
            r['violation_id'],
            r['violation_date'],
            r['plate_number'],
            (r['violation_types'][:25] + "...") if r['violation_types'] and len(r['violation_types']) > 25 else (r['violation_types'] or "N/A"),
            f"₱{r['total_fine_amount']:,.2f}",
            f"{status_color}{r['ticket_status']}{Style.RESET_ALL}",
            r['apprehending_officer'][:15] if len(r['apprehending_officer']) > 15 else r['apprehending_officer']
        ))
    
    print_table(headers, data, footer=f"Total violations: {len(rows)} | Total fines: ₱{total_fines:,.2f}")
    input("\nPress Enter to continue...")


# ── Report 6 ──────────────────────────────────────────────────────────────────
def report_violations_per_type():
    print_subheader("REPORT 6: Total Violations per Type for a Given Year")
    
    year = input(f"{Fore.CYAN}Year (e.g. 2024):{Style.RESET_ALL} ").strip()
    
    if not year or not year.isdigit():
        print_error("Please enter a valid year.")
        input("\nPress Enter to continue...")
        return

    query = """
        SELECT
            vtht.violation_type,
            COUNT(*) AS total_violations,
            SUM(vt.total_fine_amount) AS total_fines
        FROM violation_ticket vt
        JOIN violation_ticket_has_type vtht ON vt.violation_id = vtht.violation_id
        WHERE vt.year = %s
        GROUP BY vtht.violation_type
        ORDER BY total_violations DESC
    """
    rows = fetch_all(query, (year,))
    
    if not rows:
        print_warning(f"No violations found for year {year}.")
        input("\nPress Enter to continue...")
        return

    headers = ["Violation Type", "Total Violations", "Total Fines"]
    data = []
    total_violations = 0
    total_fines = 0
    for r in rows:
        total_violations += r['total_violations']
        total_fines += r['total_fines']
        data.append((
            r['violation_type'],
            r['total_violations'],
            f"₱{r['total_fines']:,.2f}"
        ))
    
    print_table(headers, data, footer=f"Year: {year} | Total violations: {total_violations} | Total fines: ₱{total_fines:,.2f}")
    input("\nPress Enter to continue...")


# ── Report 7 ──────────────────────────────────────────────────────────────────
def report_vehicles_by_location():
    print_subheader("REPORT 7: Vehicles Involved in Violations by City/Region")
    
    location = input(f"{Fore.CYAN}Enter city or region (e.g. Quezon City, Manila):{Style.RESET_ALL} ").strip()
    
    if not location:
        print_warning("Please enter a city or region.")
        input("\nPress Enter to continue...")
        return
    
    like = f"%{location}%"

    query = """
        SELECT DISTINCT
            v.plate_number,
            v.make, v.model, v.year,
            v.vehicle_type, v.color,
            CONCAT(d.first_name, ' ', d.last_name) AS owner_name,
            d.address,
            COUNT(vt.violation_id) OVER (PARTITION BY v.plate_number) AS violation_count
        FROM vehicle v
        JOIN driver d ON v.license_number = d.license_number
        JOIN violation_ticket vt ON vt.plate_number = v.plate_number
        WHERE d.address LIKE %s
        ORDER BY violation_count DESC, v.plate_number
    """
    rows = fetch_all(query, (like,))
    
    if not rows:
        print_warning(f"No vehicles found for location: {location}")
        input("\nPress Enter to continue...")
        return

    headers = ["Plate No", "Make/Model", "Year", "Type", "Color", "Owner", "Violations", "Address"]
    data = []
    for r in rows:
        make_model = f"{r['make']} {r['model']}"
        data.append((
            r['plate_number'],
            make_model[:15] if len(make_model) > 15 else make_model,
            r['year'],
            r['vehicle_type'][:15] if len(r['vehicle_type']) > 15 else r['vehicle_type'],
            r['color'],
            r['owner_name'][:18] if len(r['owner_name']) > 18 else r['owner_name'],
            r['violation_count'],
            r['address'][:25] + "..." if len(r['address']) > 25 else r['address']
        ))
    
    print_table(headers, data, footer=f"Location: {location} | Total vehicles found: {len(rows)}")
    input("\nPress Enter to continue...")