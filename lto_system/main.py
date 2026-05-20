from colorama import init, Fore, Style
from driver_menu import driver_menu
from vehicle_menu import vehicle_menu
from registration_menu import registration_menu
from violation_menu import violation_menu
from reports_menu import reports_menu
from reset_db import reset
from utils.design import clear_screen, print_success, print_error, print_warning

# Initialize colorama for Windows support
init(autoreset=True)

def print_banner():
    """Display the main menu banner"""
    clear_screen()
    print(Fore.CYAN + "╔" + "═" * 58 + "╗")
    print(Fore.CYAN + "║" + Fore.YELLOW + Style.BRIGHT + "🏛️  LTO INFORMATION MANAGEMENT SYSTEM".center(58) + Fore.CYAN + "║")
    print(Fore.CYAN + "╠" + "═" * 58 + "╣")
    print(Fore.CYAN + "║" + Fore.WHITE + " 1. Driver Management".ljust(58) + Fore.CYAN + "║")
    print(Fore.CYAN + "║" + Fore.WHITE + " 2. Vehicle Management".ljust(58) + Fore.CYAN + "║")
    print(Fore.CYAN + "║" + Fore.WHITE + " 3. Registration Management".ljust(58) + Fore.CYAN + "║")
    print(Fore.CYAN + "║" + Fore.WHITE + " 4. Violation Management".ljust(58) + Fore.CYAN + "║")
    print(Fore.CYAN + "║" + Fore.WHITE + " 5. Reports".ljust(58) + Fore.CYAN + "║")
    print(Fore.CYAN + "║" + Fore.WHITE + " 0. Exit".ljust(58) + Fore.CYAN + "║")
    print(Fore.CYAN + "╠" + "═" * 58 + "╣")
    print(Fore.CYAN + "║" + Fore.MAGENTA + " Type 'reset database' to restore original data".ljust(58) + Fore.CYAN + "║")
    print(Fore.CYAN + "╚" + "═" * 58 + "╝")
    print()

def main_menu():
    while True:
        print_banner()
        
        choice = input(f"{Fore.YELLOW}Enter choice:{Style.RESET_ALL} ").strip().lower()

        if choice == "1":
            driver_menu()
        elif choice == "2":
            vehicle_menu()
        elif choice == "3":
            registration_menu()
        elif choice == "4":
            violation_menu()
        elif choice == "5":
            reports_menu()
        elif choice == "reset database":
            print()
            reset()
            input(f"{Fore.CYAN}\nPress Enter to continue...{Style.RESET_ALL}")
        elif choice == "0":
            clear_screen()
            print(Fore.CYAN + "╔" + "═" * 58 + "╗")
            print(Fore.CYAN + "║" + Fore.GREEN + "👋 Thank you for using LTO System!".center(58) + Fore.CYAN + "║")
            print(Fore.CYAN + "╚" + "═" * 58 + "╝")
            print()
            break
        else:
            print_error("Invalid choice. Please try again.")
            input(f"{Fore.CYAN}\nPress Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    main_menu()