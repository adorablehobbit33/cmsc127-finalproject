-- ============================================================
--  LTO Information Management System
--  dummy_data.sql  –  sample data for testing
-- ============================================================

USE project;

-- ────────────────────────────────────────────────────────────
--  DRIVERS
-- ────────────────────────────────────────────────────────────

INSERT INTO driver (license_number, address, license_type, license_status, sex, date_of_birth, first_name, middle_name, last_name)
VALUES
('D000000001', '123 Rizal St., Brgy. San Antonio, Laguna',           'Non-Professional', 'valid',     'Male',   '2000-01-01', 'Juan',     'Santos',  'Dela Cruz'),
('D000000002', '45 Mabini St., Brgy. Santa Cruz, Manila',            'Professional',     'expired',   'Female', '1995-05-10', 'Maria',    NULL,      'Reyes'),
('D000000003', '789 Gorordo Ave., Brgy. Lahug, Cebu',                'Non-Professional', 'suspended', 'Male',   '1988-03-22', 'Pedro',    'Garcia',  'Lopez'),
('D000000004', '22 Rizal Ave., Brgy. Poblacion, Laguna',             'Professional',     'valid',     'Female', '1999-11-15', 'Ana',      'Torres',  'Santos'),
('D000000005', '55 JP Rizal St., Brgy. Kumintang, Batangas',         'Non-Professional', 'valid',     'Male',   '2002-07-09', 'Luis',     NULL,      'Ramos'),
('D000000006', '88 Commonwealth Ave., Brgy. Diliman, Quezon City',   'Professional',     'valid',     'Male',   '1992-08-15', 'Roberto',  'M.',      'Fernandez'),
('D000000007', '12 Jacinto St., Brgy. Obrero, Davao',                'Non-Professional', 'suspended', 'Female', '1998-12-03', 'Cristina', NULL,      'Gonzales'),
('D000000008', '7 Paseo de Roxas St., Brgy. San Lorenzo, Makati',    'Student Permit',   'valid',     'Male',   '2005-06-20', 'Mark',     'James',   'Villanueva'),
('D000000009', '34 Aguinaldo Highway, Brgy. Anabu, Cavite',          'Professional',     'expired',   'Female', '1985-09-25', 'Jennifer', 'R.',      'Ramirez'),
('D000000010', '101 MacArthur Highway, Brgy. San Nicolas, Pampanga', 'Non-Professional', 'valid',     'Male',   '1993-04-18', 'Eduardo',  'S.',      'Torres');

-- ────────────────────────────────────────────────────────────
--  DRIVER LICENSE CLASSES
-- ────────────────────────────────────────────────────────────

INSERT INTO driver_has_license_class (license_number, license_class)
VALUES
('D000000001', 'B'),
('D000000001', 'C'),
('D000000002', 'A'),
('D000000003', 'B'),
('D000000004', 'A'),
('D000000005', 'B'),
('D000000006', 'A'),
('D000000006', 'B'),
('D000000007', 'B'),
('D000000008', 'B'),
('D000000009', 'A'),
('D000000010', 'B'),
('D000000010', 'C');

-- ────────────────────────────────────────────────────────────
--  VEHICLES
-- ────────────────────────────────────────────────────────────

INSERT INTO vehicle (plate_number, chassis_number, engine_number, registration_number, color, model, year, vehicle_type, make, ownership, license_number)
VALUES
('ABC1234', 'CH001', 'EN001', 'REG001', 'Red',    'Civic',    2020, 'Car',        'Honda',      'Owned',    'D000000001'),
('XYZ5678', 'CH002', 'EN002', 'REG002', 'Blue',   'Vios',     2019, 'Car',        'Toyota',     'Owned',    'D000000002'),
('LMN8910', 'CH003', 'EN003', 'REG003', 'Black',  'Raider',   2021, 'Motorcycle', 'Suzuki',     'Owned',    'D000000003'),
('QWE4567', 'CH004', 'EN004', 'REG004', 'White',  'Hilux',    2022, 'Truck',      'Toyota',     'Owned',    'D000000001'),
('RTY2345', 'CH005', 'EN005', 'REG005', 'Gray',   'Mirage',   2018, 'Car',        'Mitsubishi', 'Owned',    'D000000004'),
('ZZA9999', 'CH006', 'EN006', 'REG006', 'Silver', 'Jazz',     2021, 'Car',        'Honda',      'Financed', 'D000000006'),
('XXB7777', 'CH007', 'EN007', 'REG007', 'Green',  'Rio',      2020, 'Car',        'Kia',        'Owned',    'D000000007'),
('YYC5555', 'CH008', 'EN008', 'REG008', 'Blue',   'Sniper',   2022, 'Motorcycle', 'Yamaha',     'Owned',    'D000000008'),
('WWD3333', 'CH009', 'EN009', 'REG009', 'Orange', 'Fortuner', 2023, 'SUV',        'Toyota',     'Financed', 'D000000009'),
('VVE1111', 'CH010', 'EN010', 'REG010', 'Brown',  'Strada',   2019, 'Truck',      'Mitsubishi', 'Owned',    'D000000010');

-- ────────────────────────────────────────────────────────────
--  VEHICLE REGISTRATIONS
--  Note: expiration_date is not a column in the schema;
--        expiry is computed at query time as registration_date + 1 YEAR.
-- ────────────────────────────────────────────────────────────

INSERT INTO vehicle_registration (registration_number, registration_date, registration_status, month, day, year, license_number, plate_number, chassis_number, engine_number)
VALUES
('REG001', '2023-01-01', 'active',   'January',   1,  2023, 'D000000001', 'ABC1234', 'CH001', 'EN001'),
('REG002', '2022-05-10', 'expired',  'May',       10, 2022, 'D000000002', 'XYZ5678', 'CH002', 'EN002'),
('REG003', '2023-07-15', 'active',   'July',      15, 2023, 'D000000003', 'LMN8910', 'CH003', 'EN003'),
('REG004', '2023-03-20', 'active',   'March',     20, 2023, 'D000000001', 'QWE4567', 'CH004', 'EN004'),
('REG005', '2021-09-01', 'expired',  'September', 1,  2021, 'D000000004', 'RTY2345', 'CH005', 'EN005'),
('REG006', '2024-01-10', 'active',   'January',   10, 2024, 'D000000006', 'ZZA9999', 'CH006', 'EN006'),
('REG007', '2023-06-20', 'expired',  'June',      20, 2023, 'D000000007', 'XXB7777', 'CH007', 'EN007'),
('REG008', '2024-02-14', 'active',   'February',  14, 2024, 'D000000008', 'YYC5555', 'CH008', 'EN008'),
('REG009', '2024-03-01', 'active',   'March',     1,  2024, 'D000000009', 'WWD3333', 'CH009', 'EN009'),
('REG010', '2022-11-05', 'expired',  'November',  5,  2022, 'D000000010', 'VVE1111', 'CH010', 'EN010');

-- ────────────────────────────────────────────────────────────
--  VIOLATION TICKETS
--  Note: location is not a column in the schema; Report 7
--        filters by city/region using the driver's address instead.
--  Note: D000000005 (Luis Ramos) is linked to RTY2345 which is
--        owned by D000000004 — valid since a driver can receive
--        a ticket while driving another person's vehicle.
-- ────────────────────────────────────────────────────────────

INSERT INTO violation_ticket (violation_id, time, total_fine_amount, month, day, year, apprehending_officer, ticket_status, license_number, plate_number, chassis_number, engine_number)
VALUES
('V001', '08:30:00', 1000.00, 'March',    10, 2024, 'Officer Cruz',      'unpaid',    'D000000001', 'ABC1234', 'CH001', 'EN001'),
('V002', '14:15:00', 2000.00, 'April',    12, 2024, 'Officer Reyes',     'paid',      'D000000002', 'XYZ5678', 'CH002', 'EN002'),
('V003', '09:00:00',  500.00, 'January',   5, 2023, 'Officer Santos',    'unpaid',    'D000000003', 'LMN8910', 'CH003', 'EN003'),
('V004', '11:45:00', 1500.00, 'February', 20, 2024, 'Officer Lim',       'paid',      'D000000001', 'QWE4567', 'CH004', 'EN004'),
('V005', '16:20:00',  750.00, 'May',       8, 2022, 'Officer Tan',       'unpaid',    'D000000004', 'RTY2345', 'CH005', 'EN005'),
('V006', '13:20:00', 2500.00, 'May',      15, 2024, 'Officer Gomez',     'unpaid',    'D000000005', 'RTY2345', 'CH005', 'EN005'),
('V007', '10:00:00',  800.00, 'June',      3, 2024, 'Officer Ramos',     'paid',      'D000000006', 'ZZA9999', 'CH006', 'EN006'),
('V008', '17:30:00', 1200.00, 'April',    22, 2024, 'Officer Fernandez', 'unpaid',    'D000000007', 'XXB7777', 'CH007', 'EN007'),
('V009', '08:00:00', 3000.00, 'March',    18, 2024, 'Officer Lopez',     'contested', 'D000000008', 'YYC5555', 'CH008', 'EN008'),
('V010', '19:45:00',  500.00, 'February', 28, 2024, 'Officer Rivera',    'paid',      'D000000009', 'WWD3333', 'CH009', 'EN009');

-- ────────────────────────────────────────────────────────────
--  VIOLATION TYPES
-- ────────────────────────────────────────────────────────────

INSERT INTO violation_ticket_has_type (violation_id, violation_type)
VALUES
('V001', 'Speeding'),
('V001', 'Reckless Driving'),
('V002', 'Illegal Parking'),
('V003', 'No Helmet'),
('V004', 'Running Red Light'),
('V005', 'Overloading'),
('V006', 'Speeding'),
('V006', 'Reckless Driving'),
('V007', 'Illegal Parking'),
('V008', 'No Seatbelt'),
('V009', 'Drunk Driving'),
('V010', 'Running Red Light');