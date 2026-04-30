from menus.driver_menu import driver_menu
from menus.vehicle_menu import vehicle_menu
from menus.registration_menu import registration_menu
from menus.violation_menu import violation_menu
# from reports.reports_menu import reports_menu

def main_menu():
    while True:
        print("\n========================================")
        print("   LTO Information Management System")
        print("========================================")
        print("1. Driver Management")
        print("2. Vehicle Management")
        print("3. Registration Management")
        print("4. Violation Management")
        print("5. Reports")
        print("0. Exit")
        print("========================================")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            driver_menu()
        elif choice == "2":
            vehicle_menu()
        elif choice == "3":
            registration_menu()
        elif choice == "4":
            violation_menu()
        # elif choice == "5":
        #     reports_menu()
        elif choice == "0":
            print("\nGoodbye!\n")
            break
        else:
            print("[!] Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()