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

    license_type   = input("License Type (Student Permit / Non-Professional / Professional): ").strip()
    license_status = input("License Status (valid / expired / suspended / revoked): ").strip()
    sex            = input("Sex (Male / Female): ").strip()
    age_min        = input("Minimum Age: ").strip()
    age_max        = input("Maximum Age: ").strip()

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
    license_number = input("Driver License Number: ").strip()

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
    as_of_date = input("As of date (YYYY-MM-DD, press Enter for today): ").strip() or "CURDATE()"

    if as_of_date == "CURDATE()":
        date_expr = "CURDATE()"
        params = []
    else:
        date_expr = "%s"
        params = [as_of_date]

    query = f"""
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
        WHERE DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) < {date_expr}
           OR vr.registration_status = 'expired'
    """
    rows = fetch_all(query, params)
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
    license_number = input("Driver License Number: ").strip()
    date_from      = input("From date (YYYY-MM-DD): ").strip()
    date_to        = input("To date   (YYYY-MM-DD): ").strip()

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
    year = input("Year (e.g. 2024): ").strip()

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
    location = input("Enter city or region (e.g. Quezon City): ").strip()
    like = f"%{location}%"

    query = """
        SELECT DISTINCT
            v.plate_number,
            v.make, v.model, v.year,
            v.vehicle_type, v.color,
            CONCAT(d.first_name, ' ', d.last_name) AS owner_name,
            d.address
        FROM vehicle v
        JOIN driver d ON v.license_number = d.license_number
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