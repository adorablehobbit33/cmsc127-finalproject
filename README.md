# LTO Information Management System

A command-line application built with **Python** and **MariaDB** that simulates a simplified version of the Land Transportation Office (LTO) operations in the Philippines. The system allows LTO personnel to manage driver records, vehicle registrations, traffic violations, and generate reports — all from the terminal.

This project was built for **CMSC 127 – File Processing and Database Systems** at the University of the Philippines Los Baños.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Requirements](#requirements)
3. [Setup Instructions](#setup-instructions)
4. [How to Use](#how-to-use)
5. [Reports Reference](#reports-reference)

---

## Project Overview

The system manages four core entities:

- **Drivers** — personal details, license information, and license status
- **Vehicles** — plate number, make/model/year, and assigned owner
- **Registrations** — registration history and expiration tracking per vehicle
- **Violations** — traffic violation tickets linked to drivers and vehicles

All data is stored in a MariaDB database. Python communicates with it through the `mysql-connector-python` library, sending raw SQL queries and displaying results back in the terminal.

```
User (Terminal)
      ↓
Python CLI  (menus, input prompts)
      ↓
mysql-connector-python
      ↓
MariaDB  (executes SQL, stores data)
```

---

## Requirements

- Python 3.8 or higher
- MariaDB (or MySQL) server running locally or remotely
- The following Python libraries:

```bash
pip install mysql-connector-python python-dotenv colorama
```

---

## Setup Instructions

### 1. Clone or download the project

Place all files in a folder, for example `lto_system/`.

### 2. Create the database

Open your MariaDB client (e.g. via terminal or DBeaver) and run the full setup script:

```bash
mariadb -u your_user -p < sql/setup.sql
```

This will:
- Drop and recreate the `project` database
- Create all 6 tables with proper keys and constraints
- Create all 7 views used for reports

### 3. Create your `.env` file

In the root of the project folder, create a file named `.env` with your local database credentials:

```
DB_HOST=localhost
DB_USER=your_mariadb_username
DB_PASSWORD=your_mariadb_password
DB_NAME=project
```

> **Important:** Never share or commit your `.env` file. It is specific to your local machine.

### 4. Load sample data

There's a provided `dummy_data.sql` file is available, you can load it to populate the database with test records:

```bash
mariadb -u your_user -p project < sql/dummy_data.sql
```

### 5. Run the program

```bash
python main.py
```

---

## How to Use

### Main Menu

When you run `main.py`, the following menu appears:

```
========================================
   LTO Information Management System
========================================
1. Driver Management
2. Vehicle Management
3. Registration Management
4. Violation Management
5. Reports
0. Exit
========================================
Enter choice:
```

Type a number and press **Enter** to navigate. Type `0` at any menu to go back or exit.

---

### Driver Management

Manages driver records in the `driver` table.

| Option | What it does |
|--------|-------------|
| 1. Add Driver | Prompts for all driver details and inserts a new record |
| 2. Update Driver | Looks up a driver by license number; lets you update address, license type, and status |
| 3. Delete Driver | Looks up a driver, asks for confirmation, then deletes the record |
| 4. Search Driver | Searches by partial name or license number; prints a formatted table |

**Key fields when adding a driver:**

- `License Number` — format: `N01-23-456789`
- `License Type` — one of: `Student Permit`, `Non-Professional`, `Professional`
- `License Status` — one of: `valid`, `expired`, `suspended`, `revoked`
- `Date of Birth` — format: `YYYY-MM-DD`
- `Sex` — `Male` or `Female`

---

### Vehicle Management

Manages vehicle records in the `vehicle` table.

| Option | What it does |
|--------|-------------|
| 1. Add Vehicle | Prompts for plate number, make, model, year, type, color, and owner |
| 2. Update Vehicle | Looks up by plate number; lets you update color, type, and ownership |
| 3. Delete Vehicle | Looks up by plate number, confirms, then deletes |
| 4. Search Vehicle | Searches by plate number, make, or model |

**Key fields when adding a vehicle:**

- `Plate Number` — format: `ABC1234`
- `Vehicle Type` — one of: `motorcycle`, `private car`, `public utility vehicle`
- `Owner License Number` — must match an existing driver's license number

---

### Registration Management

Manages vehicle registration records in the `vehicle_registration` table.

| Option | What it does |
|--------|-------------|
| 1. Add Registration | Records a new registration for a vehicle |
| 2. Update Registration | Updates the registration status |
| 3. Delete Registration | Removes a registration record |
| 4. Search Registration | Searches by registration number or plate number; shows expiry date |

**Key fields when adding a registration:**

- `Registration Date` — format: `YYYY-MM-DD` (expiration is automatically computed as +1 year)
- `Status` — one of: `active`, `expired`, `suspended`
- `Plate Number` — must match an existing vehicle

---

### Violation Management

Manages traffic violation tickets in the `violation_ticket` and `violation_ticket_has_type` tables.

| Option | What it does |
|--------|-------------|
| 1. Add Violation | Records a new violation ticket and its type(s) |
| 2. Update Violation | Updates the ticket status and/or fine amount |
| 3. Delete Violation | Removes the ticket and its associated type entries |
| 4. Search Violation | Searches by violation ID or license number |

**Key fields when adding a violation:**

- `Date` — format: `YYYY-MM-DD`
- `Time` — format: `HH:MM:SS`
- `Ticket Status` — one of: `unpaid`, `paid`, `contested`
- `Violation Type` — e.g., `overspeeding`, `reckless driving`, `illegal parking`
- `Apprehending Officer` — optional; leave blank to default to `Unknown`

---

### Reports

Generates read-only reports from the database. No data is modified here.

```
--- Reports ---
1. Drivers filtered by license type, status, age range, sex
2. Vehicles owned by a driver
3. Vehicles with expired registrations as of a given date
4. Drivers with expired or suspended licenses
5. Violations by a driver within a date range
6. Total violations per type for a given year
7. Vehicles involved in violations within a city or region
0. Back
```

All filter fields are optional — press **Enter** to skip a filter and return unfiltered results. See the [Reports Reference](#reports-reference) section below for details on each report.

---

## Reports Reference

| # | Report | Key Input(s) |
|---|--------|-------------|
| 1 | Filtered drivers | License type, status, sex, min/max age (all optional) |
| 2 | Vehicles by driver | Driver's license number |
| 3 | Expired registrations | As-of date (defaults to today) |
| 4 | Invalid licenses | None — returns all expired/suspended drivers |
| 5 | Violations by driver | License number, date range (`YYYY-MM-DD`) |
| 6 | Violations by type | Year (e.g., `2024`) |
| 7 | Vehicles by location | City or region keyword (e.g., `Quezon City`) |

> Report 7 matches against the **driver's address** field, since violation location is stored as part of the driver's registered address in this schema.