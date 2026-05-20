from datetime import datetime

from db import fetch_all

def reports_menu():
    while True:
        print("\n--- Reports ---")
        print("1. Drivers filtered by license type, status, age range, sex")
        print("2. Vehicles owned by a driver")
        print("3. Vehicles with expired registrations as of a given date")
        print("4. Drivers with expired or suspended licenses")
        print("5. Violations by a driver within a date range")
        print("6. Total violations per type for a given year")
        print("7. Vehicles involved in violations within a city or region")
        print("0. Back")

        choice = input("Enter choice: ").strip()

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
            print("[!] Invalid choice.")


# ── Report 1 ──────────────────────────────────────────────────────────────────
def report_drivers_filtered():
    print("\n-- Report: Filtered Drivers --")
    print("(Press Enter to skip any filter)\n")

    allowed_types = ["student permit", "non-professional", "professional"]

    while True:
        license_type = input("License Type (Student Permit / Non-Professional / Professional): ").strip()
        if not license_type:
            break
        if license_type.lower() in allowed_types:
            # Re-assign exact capitalization match
            license_type = next(t for t in ["Student Permit", "Non-Professional", "Professional"] if t.lower() == license_type.lower())
            break
        print(f"[!] Error: Invalid type. Choose from: Student Permit, Non-Professional, Professional")
    allowed_statuses = ["valid", "expired", "suspended", "revoked"]

    while True:
        license_status = input("License Status (valid / expired / suspended / revoked): ").strip().lower()
        if not license_status or license_status in allowed_statuses:
            break
        print(f"[!] Error: Invalid status. Choose from: {', '.join(allowed_statuses)}")

    while True:
        sex = input("Sex (Male / Female): ").strip()
        if not sex:
            break
        if sex.lower() in ["male", "female"]:
            sex = "Male" if sex.lower() == "male" else "Female"
            break
        print("[!] Error: Sex filter parameter must be exactly 'Male' or 'Female'.")

    while True:
        age_min = input("Minimum Age: ").strip()
        if not age_min:
            break
        if age_min.isdigit() and int(age_min) >= 0:
            break
        print("[!] Error: Minimum age metric must be a positive integer.")

    while True:
        age_max = input("Maximum Age: ").strip()
        if not age_max:
            break
        if age_max.isdigit() and int(age_max) >= 0:
            if age_min and int(age_max) < int(age_min):
                print("[!] Error: Maximum boundary metric cannot be less than Minimum constraint age.")
                continue
            break
        print("[!] Error: Maximum age metric must be a positive integer.")

    query = """
        SELECT
            license_number,
            CONCAT(first_name, ' ', COALESCE(middle_name, ''), ' ', last_name) AS full_name,
            date_of_birth,
            sex,
            address,
            license_type,
            license_status,
            YEAR(CURDATE()) - YEAR(date_of_birth) -
              (DATE_FORMAT(CURDATE(),'%m%d') < DATE_FORMAT(date_of_birth,'%m%d')) AS age
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
        query += """
            AND (YEAR(CURDATE()) - YEAR(date_of_birth) -
              (DATE_FORMAT(CURDATE(),'%m%d') < DATE_FORMAT(date_of_birth,'%m%d'))) >= %s
        """
        params.append(int(age_min))
    if age_max:
        query += """
            AND (YEAR(CURDATE()) - YEAR(date_of_birth) -
              (DATE_FORMAT(CURDATE(),'%m%d') < DATE_FORMAT(date_of_birth,'%m%d'))) <= %s
        """
        params.append(int(age_max))

    rows = fetch_all(query, params)
    if not rows:
        print("[!] No drivers found.")
        return

    print(f"\n{'License No.':<15} {'Full Name':<30} {'Type':<22} {'Status':<12} {'Sex':<8} {'Age':<5}")
    print("-" * 95)
    for r in rows:
        print(f"{r['license_number']:<15} {r['full_name']:<30} {r['license_type']:<22} "
              f"{r['license_status']:<12} {r['sex']:<8} {r['age']:<5}")


# ── Report 2 ──────────────────────────────────────────────────────────────────
def report_vehicles_by_driver():
    print("\n-- Report: Vehicles by Driver --")
    while True:
        license_number = input("Driver License Number: ").strip()
        if not license_number:
            print("[!] Error: Driver license target reference cannot be empty.")
            continue
        break

    driver_exists = fetch_all("SELECT license_number FROM driver WHERE license_number = %s", (license_number,))
    if not driver_exists:
        print("[!] Error: No driver found with that license number in database ledger.")
        return
    
    query = """
        SELECT
            v.plate_number, v.make, v.model, v.year,
            v.color, v.vehicle_type, v.chassis_number, v.engine_number
        FROM vehicle v
        WHERE v.license_number = %s
    """
    rows = fetch_all(query, (license_number,))
    if not rows:
        print("[!] No vehicles found for that driver.")
        return

    print(f"\n{'Plate No.':<10} {'Make':<12} {'Model':<12} {'Year':<6} {'Color':<12} {'Type':<22}")
    print("-" * 80)
    for r in rows:
        print(f"{r['plate_number']:<10} {r['make']:<12} {r['model']:<12} "
              f"{str(r['year']):<6} {r['color']:<12} {r['vehicle_type']:<22}")


# ── Report 3 ──────────────────────────────────────────────────────────────────
def report_expired_registrations():
    print("\n-- Report: Vehicles with Expired Registrations --")
    while True:
        as_of_input = input("As of date (YYYY-MM-DD, press Enter for today): ").strip()
        if not as_of_input:
            target_date = datetime.now().strftime("%Y-%m-%d")
            break
        try:
            datetime.strptime(as_of_input, "%Y-%m-%d")
            target_date = as_of_input
            break
        except ValueError:
            print("[!] Error: Invalid calendar format. Please write exactly as YYYY-MM-DD.")
    query = """
        SELECT
            vr.registration_number,
            vr.plate_number,
            v.make, v.model, v.year,
            vr.registration_date,
            DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) AS expiration_date,
            vr.registration_status,
            COALESCE(CONCAT(d.first_name, ' ', d.last_name), 'Unassigned Entity') AS owner_name
        FROM vehicle_registration vr
        JOIN vehicle v ON vr.plate_number = v.plate_number
        LEFT JOIN driver  d ON vr.license_number = d.license_number
        WHERE DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) < %s
           OR vr.registration_status = 'expired'
    """
    rows = fetch_all(query, (target_date,))
    if not rows:
        print("[!] No expired registrations found.")
        return

    print(f"\n{'Reg No.':<10} {'Plate No.':<10} {'Make/Model':<20} {'Reg Date':<14} {'Expiry':<14} {'Owner':<25}")
    print("-" * 98)
    for r in rows:
        make_model = f"{r['make']} {r['model']}"
        print(f"{r['registration_number']:<10} {r['plate_number']:<10} {make_model:<20} "
              f"{str(r['registration_date']):<14} {str(r['expiration_date']):<14} {r['owner_name']:<25}")


# ── Report 4 ──────────────────────────────────────────────────────────────────
def report_invalid_licenses():
    print("\n-- Report: Drivers with Expired or Suspended Licenses --")

    query = """
        SELECT
            license_number,
            CONCAT(first_name, ' ', last_name) AS driver_name,
            license_type, license_status, date_of_birth, address
        FROM driver
        WHERE license_status IN ('expired', 'suspended')
        ORDER BY license_status, last_name
    """
    rows = fetch_all(query)
    if not rows:
        print("[!] No drivers with expired or suspended licenses.")
        return

    print(f"\n{'License No.':<15} {'Driver Name':<28} {'Type':<22} {'Status':<12}")
    print("-" * 80)
    for r in rows:
        print(f"{r['license_number']:<15} {r['driver_name']:<28} "
              f"{r['license_type']:<22} {r['license_status']:<12}")


# ── Report 5 ──────────────────────────────────────────────────────────────────
def report_violations_by_driver():
    print("\n-- Report: Violations by Driver within Date Range --")
    while True:
        license_number = input("Driver License Number: ").strip()
        if not license_number:
            print("[!] Error: Driver license target reference cannot be empty.")
            continue
        break
    while True:
        date_from = input("From date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(date_from, "%Y-%m-%d")
            break
        except ValueError:
            print("[!] Error: Invalid start date format. Please write exactly as YYYY-MM-DD.")
            
    while True:
        date_to = input("To date   (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(date_to, "%Y-%m-%d")
            if date_to < date_from:
                print("[!] Error: End date cannot be chronologically prior to Start date parameters.")
                continue
            break
        except ValueError:
            print("[!] Error: Invalid end date format. Please write exactly as YYYY-MM-DD.")

    query = """
        SELECT
            vt.violation_id,
            vt.ticket_status,
            vt.total_fine_amount,
            vt.apprehending_officer,
            vt.plate_number,
            STR_TO_DATE(CONCAT(vt.year,'-',TRIM(vt.month),'-',vt.day), '%Y-%M-%d') AS violation_date,
            COALESCE(GROUP_CONCAT(vtht.violation_type SEPARATOR ', '), 'Unclassified') AS violation_types
        FROM violation_ticket vt
        LEFT JOIN violation_ticket_has_type vtht ON vt.violation_id = vtht.violation_id
        WHERE vt.license_number = %s
          AND STR_TO_DATE(CONCAT(vt.year,'-',TRIM(vt.month),'-',vt.day), '%Y-%M-%d')
              BETWEEN %s AND %s
        GROUP BY vt.violation_id
        ORDER BY violation_date
    """
    rows = fetch_all(query, (license_number, date_from, date_to))
    if not rows:
        print("[!] No violations found for that driver in the given range.")
        return

    print(f"\n{'Violation ID':<15} {'Date':<14} {'Type(s)':<30} {'Fine':<10} {'Status':<12}")
    print("-" * 85)
    for r in rows:
        print(f"{r['violation_id']:<15} {str(r['violation_date']):<14} "
              f"{str(r['violation_types']):<30} {str(r['total_fine_amount']):<10} {r['ticket_status']:<12}")


# ── Report 6 ──────────────────────────────────────────────────────────────────
def report_violations_per_type():
    print("\n-- Report: Total Violations per Type for a Given Year --")
    while True:
        year = input("Year (e.g. 2024): ").strip()
        if year.isdigit() and len(year) == 4:
            break
        print("[!] Error: Please provide a valid 4-digit calendar year value.")

    query = """
        SELECT
            vtht.violation_type,
            COUNT(*) AS total_violations
        FROM violation_ticket vt
        JOIN violation_ticket_has_type vtht ON vt.violation_id = vtht.violation_id
        WHERE vt.year = %s
        GROUP BY vtht.violation_type
        ORDER BY total_violations DESC
    """
    rows = fetch_all(query, (year,))
    if not rows:
        print(f"[!] No violations found for year {year}.")
        return

    print(f"\n{'Violation Type':<35} {'Total':<10}")
    print("-" * 48)
    for r in rows:
        print(f"{r['violation_type']:<35} {r['total_violations']:<10}")


# ── Report 7 ──────────────────────────────────────────────────────────────────
def report_vehicles_by_location():
    print("\n-- Report: Vehicles Involved in Violations by City/Region --")
    while True:
        location = input("Enter city or region name to filter (e.g. Quezon City): ").strip()
        if not location:
            print("[!] Error: Search location arguments cannot be left empty.")
            continue
        break
    like = f"%{location}%"

    query = """
        SELECT DISTINCT
            v.plate_number,
            v.make, v.model, v.year,
            v.vehicle_type, v.color,
            CONCAT(d.first_name, ' ', d.last_name) AS owner_name,
            d.address
        FROM vehicle v
        LEFT JOIN driver d ON v.license_number = d.license_number
        JOIN violation_ticket vt ON vt.plate_number = v.plate_number
        WHERE d.address LIKE %s 
        ORDER BY v.plate_number
    """
    rows = fetch_all(query, (like,))
    if not rows:
        print(f"[!] No vehicles found for location: {location}")
        return

    print(f"\n{'Plate No.':<10} {'Make':<10} {'Model':<12} {'Year':<6} {'Type':<22} {'Owner':<25}")
    print("-" * 90)
    for r in rows:
        print(f"{r['plate_number']:<10} {r['make']:<10} {r['model']:<12} "
              f"{str(r['year']):<6} {r['vehicle_type']:<22} {r['owner_name']:<25}")