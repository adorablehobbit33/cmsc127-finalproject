# utils/design.py
import sys
import os
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows support
init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    clear_screen()
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + "🏛️  LTO INFORMATION MANAGEMENT SYSTEM".center(60))
    print(Fore.CYAN + "=" * 60)
    print(Fore.WHITE + f"📋 {title}".center(60))
    print(Fore.CYAN + "-" * 60)
    print(Style.RESET_ALL)

def print_success(msg):
    print(Fore.GREEN + f"✅ {msg}")

def print_error(msg):
    print(Fore.RED + f"❌ {msg}")

def print_info(msg):
    print(Fore.BLUE + f"ℹ️  {msg}")

def print_warning(msg):
    print(Fore.YELLOW + f"⚠️  {msg}")

def print_table(headers, rows, footer=None):
    if not rows:
        print_warning("No data found.")
        return
    
    col_widths = []
    for i, header in enumerate(headers):
        max_len = len(header)
        for row in rows:
            if i < len(row):
                max_len = max(max_len, len(str(row[i])))
        col_widths.append(min(max_len + 2, 40))
    
    print(Fore.CYAN + "┌" + "┬".join("─" * w for w in col_widths) + "┐")
    
    header_line = "│"
    for i, header in enumerate(headers):
        header_line += f" {header:<{col_widths[i]-1}}│"
    print(Fore.YELLOW + Style.BRIGHT + header_line + Style.RESET_ALL)
    
    print(Fore.CYAN + "├" + "┼".join("─" * w for w in col_widths) + "┤")
    
    for row in rows:
        row_line = "│"
        for i, col in enumerate(row):
            if i < len(col_widths):
                cell = str(col) if col is not None else ""
                if len(cell) > col_widths[i] - 1:
                    cell = cell[:col_widths[i] - 4] + "..."
                row_line += f" {cell:<{col_widths[i]-1}}│"
        print(Fore.WHITE + row_line)
    
    print(Fore.CYAN + "└" + "┴".join("─" * w for w in col_widths) + "┘")
    
    if footer:
        print(Fore.GREEN + f"\n{footer}")

def print_divider():
    print(Fore.CYAN + "─" * 60)

def print_subheader(text):
    print(Fore.MAGENTA + f"\n▶ {text}")
    print(Fore.CYAN + "─" * 40)

def input_required(prompt, field_name="This field"):
    while True:
        value = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}").strip()
        if value:
            return value
        print_error(f"{field_name} is required.")

def input_option(prompt, options, default=None):
    print(Fore.CYAN + prompt)
    for i, opt in enumerate(options, 1):
        print(f"  {Fore.YELLOW}{i}.{Style.RESET_ALL} {opt}")
    
    while True:
        choice = input(f"{Fore.CYAN}Choose (1-{len(options)}){Style.RESET_ALL}: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        if default is not None:
            return default
        print_error(f"Invalid choice. Please enter 1-{len(options)}.")

def input_date(prompt, default=""):
    import datetime
    while True:
        date_str = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}").strip()
        if not date_str and default:
            return default
        if date_str:
            try:
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
                return date_str
            except ValueError:
                print_error("Invalid date format. Use YYYY-MM-DD")
        else:
            print_error("Please enter a date in YYYY-MM-DD format")

def input_license_number():
    print_info("License Number format: D000000001 (D + 9 digits)")
    return input_required("License Number: ", "License number")

def input_plate_number():
    print_info("Plate Number format: ABC1234 (3 letters + 4 numbers)")
    return input_required("Plate Number: ", "Plate number")

def clear_screen():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')