from db import execute_query, fetch_all

def vehicle_menu():
    while True:
        print("\n--- Vehicle Management ---")
        print("1. Add Vehicle")
        print("2. Update Vehicle")
        print("3. Delete Vehicle")
        print("4. Search Vehicle")
        print("5. Print All Vehicles")
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
        elif choice == "5":
            print_all_vehicles()
        elif choice == "0":
            break
        else:
            print("[!] Invalid choice.")

def add_vehicle():
    print("\n-- Add Vehicle --")
    

    while True:
        plate_number = input("Plate Number (e.g. ABC1234): ").strip()
        if len(plate_number) == 0:
            print("[!] Error: Plate number cannot be empty.")
        elif len(plate_number) > 7:
            print(f"[!] Error: Input too long ({len(plate_number)} chars). Max allowed is 7.")
        else:
            break

    while True:
        chassis_number = input("Chassis Number: ").strip()
        if len(chassis_number) == 0:
            print("[!] Error: Chassis number cannot be empty.")
        elif len(chassis_number) > 17:
            print(f"[!] Error: Input too long ({len(chassis_number)} chars). Max allowed is 17.")
        else:
            break


    while True:
        engine_number = input("Engine Number: ").strip()
        if len(engine_number) == 0:
            print("[!] Error: Engine number cannot be empty.")
        elif len(engine_number) > 17:
            print(f"[!] Error: Input too long ({len(engine_number)} chars). Max allowed is 17.")
        else:
            break

    while True:
        registration_number = input("Registration Number: ").strip()
        if len(registration_number) == 0:
            print("[!] Error: Registration number cannot be empty.")
        elif len(registration_number) > 7:
            print(f"[!] Error: Input too long ({len(registration_number)} chars). Max allowed is 7.")
        else:
            break

   
    while True:
        color = input("Color: ").strip()
        if len(color) == 0:
            print("[!] Error: Color cannot be empty.")
        elif len(color) > 50:
            print(f"[!] Error: Input too long ({len(color)} chars). Max allowed is 50.")
        else:
            break

   
    while True:
        make = input("Make (e.g. Toyota): ").strip()
        if len(make) == 0:
            print("[!] Error: Make cannot be empty.")
        elif len(make) > 50:
            print(f"[!] Error: Input too long ({len(make)} chars). Max allowed is 50.")
        else:
            break

   
    while True:
        model = input("Model (e.g. Vios): ").strip()
        if len(model) == 0:
            print("[!] Error: Model cannot be empty.")
        elif len(model) > 50:
            print(f"[!] Error: Input too long ({len(model)} chars). Max allowed is 50.")
        else:
            break

    while True:
        year_input = input("Year (e.g. 2020): ").strip()
        if len(year_input) == 0:
            print("[!] Error: Year cannot be empty.")
            continue
        try:
            year = int(year_input)
            if year < 1900 or year > 2026: # Closes future anomaly edge case entries
                print("[!] Error: Please enter a realistic automobile manufacturing year (1900-2026).")
            else:
                break
        except ValueError:
            print("[!] Error: Year must be a valid numerical integer.")

    # 9. Vehicle Type Validation (Strictly capped below your VARCHAR(10) table constraint!)
    allowed_types = ["motorcycle", "private", "public"]
    while True:
        vehicle_type = input("Vehicle Type (motorcycle/private/public): ").strip().lower()
        if len(vehicle_type) == 0:
            print("[!] Error: Vehicle type cannot be empty.")
        elif vehicle_type not in allowed_types:
            print(f"[!] Error: Choice must be exactly one of: {', '.join(allowed_types)}")
        else:
            break

    while True:
        ownership = input("Ownership Name (leave blank if none): ").strip() or None
        if ownership and len(ownership) > 50:
            print(f"[!] Error: Name string too long ({len(ownership)} chars). Max allowed is 50.")
        else:
            break

    while True:
        license_number = input("Owner License Number (leave blank if none): ").strip() or None
        if license_number and len(license_number) > 13:
            print(f"[!] Error: License input too long ({len(license_number)} chars). Max allowed is 13.")
        else:
            break

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
    while True:
        plate_number = input("Plate Number (e.g. ABC1234): ").strip()
        if len(plate_number) == 0:
            print("[!] Error: Plate number cannot be empty.")
        elif len(plate_number) > 7:
            print(f"[!] Error: Input too long ({len(plate_number)} chars). Max allowed is 7.")
        else:
            break


    rows = fetch_all("SELECT * FROM vehicle WHERE plate_number = %s", (plate_number,))
    if not rows:
        print("[!] Vehicle not found.")
        return

    v = rows[0]
    print(f"\nCurrent info: {v['make']} {v['model']} {v['year']} | {v['color']} | {v['vehicle_type']}")
    print("(Press Enter to keep current value)\n")

    while True:
        color_input = input(f"Color [{v['color']}]: ").strip()
        color = color_input if color_input else v['color']
        if len(color) == 0:
            print("[!] Error: Color cannot be left completely empty.")
        elif len(color) > 50:
            print(f"[!] Error: Color input too long ({len(color)} chars). Max allowed is 50.")
        else:
            break

    allowed_types = ["motorcycle", "private", "public"]
    while True:
        type_input = input(f"Vehicle Type [{v['vehicle_type']}]: ").strip().lower()
        vehicle_type = type_input if type_input else v['vehicle_type']
        if vehicle_type not in allowed_types:
            print(f"[!] Error: Choice must be exactly one of: {', '.join(allowed_types)}")
        else:
            break
        
    while True:
        ownership_input = input(f"Ownership [{v['ownership'] if v['ownership'] else 'None'}]: ").strip()
        
        if ownership_input.lower() == "none":
            ownership = None
            break

        ownership = ownership_input if ownership_input else v['ownership']
        if ownership and len(ownership) > 50:
            print(f"[!] Error: Ownership string too long ({len(ownership)} chars). Max allowed is 50.")
        else:
            break

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
    while True:
        plate_number = input("Enter plate number to delete(e.g. ABC1234): ").strip()
        if len(plate_number) == 0:
            print("[!] Error: Plate number cannot be empty.")
        elif len(plate_number) > 7:
            print(f"[!] Error: Input too long ({len(plate_number)} chars). Max allowed is 7.")
        else:
            break

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
    while True:
        keyword = input("Enter plate number, make, or model to search: ").strip()
        if not keyword:
            print("[!] Error: Search field cannot be empty.")
            continue
        break
    like = f"%{keyword}%"

    query = """
        SELECT v.plate_number, v.make, v.model, v.year, v.color, v.vehicle_type,
               COALESCE(CONCAT(d.first_name,' ',d.last_name), 'Unassigned') AS owner_name
        FROM vehicle v
        LEFT JOIN driver d ON v.license_number = d.license_number
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
    
def print_all_vehicles():
    print("\n-- All Registered Vehicles --")
    query = """
        SELECT v.plate_number, v.make, v.model, v.year, v.color, v.vehicle_type,
            CONCAT(d.first_name, ' ', d.last_name) AS owner_name
        FROM vehicle v
        LEFT JOIN driver d ON v.license_number = d.license_number
        ORDER BY v.plate_number
    """
    rows = fetch_all(query)

    if not rows:
        print("[!] No vehicles registered in the system.")
        return

    print(f"\n{'Plate No.':<12} {'Make/Model':<20} {'Year':<6} {'Color':<10} {'Type':<15} {'Owner':<20}")
    print("-" * 100)
    for r in rows:
        make_model = f"{r['make']} {r['model']}"
        owner = r['owner_name'] if r['owner_name'] else "Unassigned"
        print(f"{r['plate_number']:<12} {make_model:<20} {r['year']:<6} {r['color']:<10} {r['vehicle_type']:<15} {owner:<20}")