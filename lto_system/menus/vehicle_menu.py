from db import execute_query, fetch_all

def vehicle_menu():
    while True:
        print("\n--- Vehicle Management ---")
        print("1. Add Vehicle")
        print("2. Update Vehicle")
        print("3. Delete Vehicle")
        print("4. Search Vehicle")
        print("0. Back")

        choice = input("Enter choice: ").strip()

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
            print("[!] Invalid choice.")

def add_vehicle():
    print("\n-- Add Vehicle --")
    plate_number = input("Plate Number (e.g. ABC1234): ").strip()
    chassis_number = input("Chassis Number: ").strip()
    engine_number = input("Engine Number: ").strip()
    registration_number = input("Registration Number: ").strip()
    color = input("Color: ").strip()
    make = input("Make (e.g. Toyota): ").strip()
    model = input("Model (e.g. Vios): ").strip()
    year = input("Year (e.g. 2020): ").strip()
    vehicle_type = input("Vehicle Type (motorcycle/private car/public utility vehicle): ").strip()
    ownership = input("Ownership (e.g. name or license number): ").strip()
    license_number = input("Owner License Number: ").strip()

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
        print("[✓] Vehicle added successfully.")
    else:
        print(f"[✗] Failed: {msg}")

def update_vehicle():
    print("\n-- Update Vehicle --")
    plate_number = input("Enter Plate Number of vehicle to update: ").strip()

    rows = fetch_all("SELECT * FROM vehicle WHERE plate_number = %s", (plate_number,))
    if not rows:
        print("[!] Vehicle not found.")
        return

    v = rows[0]
    print(f"\nCurrent info: {v['make']} {v['model']} {v['year']} | {v['color']} | {v['vehicle_type']}")
    print("(Press Enter to keep current value)\n")

    color = input(f"Color [{v['color']}]: ").strip() or v['color']
    vehicle_type = input(f"Vehicle Type [{v['vehicle_type']}]: ").strip() or v['vehicle_type']
    ownership = input(f"Ownership [{v['ownership']}]: ").strip() or v['ownership']

    query = """
        UPDATE vehicle
        SET color = %s, vehicle_type = %s, ownership = %s
        WHERE plate_number = %s
    """
    success, msg = execute_query(query, (color, vehicle_type, ownership, plate_number))

    if success:
        print("[✓] Vehicle updated successfully.")
    else:
        print(f"[✗] Failed: {msg}")

def delete_vehicle():
    print("\n-- Delete Vehicle --")
    plate_number = input("Enter Plate Number of vehicle to delete: ").strip()

    rows = fetch_all("SELECT * FROM vehicle WHERE plate_number = %s", (plate_number,))
    if not rows:
        print("[!] Vehicle not found.")
        return

    v = rows[0]
    confirm = input(f"Delete {v['make']} {v['model']} ({v['plate_number']})? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("[!] Cancelled.")
        return

    success, msg = execute_query("DELETE FROM vehicle WHERE plate_number = %s", (plate_number,))
    if success:
        print("[✓] Vehicle deleted successfully.")
    else:
        print(f"[✗] Failed: {msg}")

def search_vehicle():
    print("\n-- Search Vehicle --")
    keyword = input("Enter plate number, make, or model to search: ").strip()
    like = f"%{keyword}%"

    query = """
        SELECT v.plate_number, v.make, v.model, v.year, v.color, v.vehicle_type,
               CONCAT(d.first_name, ' ', d.last_name) AS owner_name
        FROM vehicle v
        JOIN driver d ON v.license_number = d.license_number
        WHERE v.plate_number LIKE %s
           OR v.make LIKE %s
           OR v.model LIKE %s
    """
    rows = fetch_all(query, (like, like, like))

    if not rows:
        print("[!] No vehicles found.")
        return

    print(f"\n{'Plate No.':<10} {'Make':<12} {'Model':<12} {'Year':<6} {'Color':<12} {'Type':<20} {'Owner':<25}")
    print("-" * 100)
    for r in rows:
        print(f"{r['plate_number']:<10} {r['make']:<12} {r['model']:<12} {str(r['year']):<6} {r['color']:<12} {r['vehicle_type']:<20} {r['owner_name']:<25}")