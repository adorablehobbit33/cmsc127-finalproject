-- ============================================================
--  LTO Information Management System
--  setup.sql  –  tables + views
-- ============================================================

DROP DATABASE IF EXISTS project;
CREATE DATABASE IF NOT EXISTS project;
USE project;

-- ────────────────────────────────────────────────────────────
--  TABLES
-- ────────────────────────────────────────────────────────────

-- Table 1: Driver
CREATE TABLE driver (
    license_number  VARCHAR(13)  PRIMARY KEY,
    address         VARCHAR(255) NOT NULL,
    license_type    VARCHAR(50)  NOT NULL,
    license_status  VARCHAR(15)  NOT NULL,
    sex             VARCHAR(10)  NOT NULL,
    date_of_birth   DATE         NOT NULL,
    first_name      VARCHAR(50)  NOT NULL,
    middle_name     VARCHAR(50),
    last_name       VARCHAR(50)  NOT NULL
);

-- Table 2: Driver license classes (1 driver → many classes)
CREATE TABLE driver_has_license_class (
    license_number  VARCHAR(13),
    license_class   VARCHAR(20),
    PRIMARY KEY (license_number, license_class),
    FOREIGN KEY (license_number) REFERENCES driver(license_number)
        ON DELETE CASCADE
);

-- Table 3: Violation ticket
CREATE TABLE violation_ticket (
    violation_id          VARCHAR(20)    PRIMARY KEY,
    time                  TIME           NOT NULL,
    total_fine_amount     DECIMAL(10,2)  NOT NULL,
    month                 VARCHAR(10)    NOT NULL,
    day                   INT            NOT NULL,
    year                  INT            NOT NULL,
    apprehending_officer  VARCHAR(255)   NOT NULL DEFAULT 'Unknown',
    ticket_status         VARCHAR(20)    NOT NULL,
    license_number        VARCHAR(13),
    plate_number          VARCHAR(7),
    chassis_number        VARCHAR(17),
    engine_number         VARCHAR(17),
    FOREIGN KEY (license_number) REFERENCES driver(license_number)
        ON DELETE SET NULL
);

-- Table 4: Violation ticket types (1 ticket → many types)
CREATE TABLE violation_ticket_has_type (
    violation_id    VARCHAR(20),
    violation_type  VARCHAR(50),
    PRIMARY KEY (violation_id, violation_type),
    FOREIGN KEY (violation_id) REFERENCES violation_ticket(violation_id)
        ON DELETE CASCADE
);

-- Table 5: Vehicle
CREATE TABLE vehicle (
    plate_number         VARCHAR(7)   PRIMARY KEY,
    chassis_number       VARCHAR(17)  NOT NULL,
    engine_number        VARCHAR(17)  NOT NULL,
    registration_number  VARCHAR(7)   NOT NULL,
    color                VARCHAR(50)  NOT NULL,
    model                VARCHAR(50)  NOT NULL,
    year                 INT          NOT NULL,
    vehicle_type         VARCHAR(50)  NOT NULL,
    make                 VARCHAR(50)  NOT NULL,
    ownership            VARCHAR(50),
    license_number       VARCHAR(13),
    FOREIGN KEY (license_number) REFERENCES driver(license_number)
        ON DELETE SET NULL
);

-- Table 6: Vehicle registration
CREATE TABLE vehicle_registration (
    registration_number  VARCHAR(7)   PRIMARY KEY,
    registration_date    DATE         NOT NULL,
    registration_status  VARCHAR(20)  NOT NULL,
    month                VARCHAR(10)  NOT NULL,
    day                  INT          NOT NULL,
    year                 INT          NOT NULL,
    license_number       VARCHAR(13),
    plate_number         VARCHAR(7),
    chassis_number       VARCHAR(17),
    engine_number        VARCHAR(17),
    FOREIGN KEY (license_number) REFERENCES driver(license_number)
        ON DELETE SET NULL,
    FOREIGN KEY (plate_number)   REFERENCES vehicle(plate_number)
        ON DELETE SET NULL
);

ALTER TABLE violation_ticket
  ADD CONSTRAINT fk_vt_plate
  FOREIGN KEY (plate_number) REFERENCES vehicle(plate_number)
  ON DELETE SET NULL;
-- ────────────────────────────────────────────────────────────
--  VIEWS
-- ────────────────────────────────────────────────────────────

-- View 1: Drivers with computed age (filter at query time)
CREATE VIEW view_driver_filtered AS
SELECT
    license_number,
    CONCAT(first_name, ' ', COALESCE(middle_name, ''), ' ', last_name) AS full_name,
    date_of_birth,
    sex,
    address,
    license_type,
    license_status,
    YEAR(CURDATE()) - YEAR(date_of_birth) -
        (DATE_FORMAT(CURDATE(), '%m%d') < DATE_FORMAT(date_of_birth, '%m%d')) AS age
FROM driver;

-- View 2: All vehicles with owner name
CREATE VIEW view_vehicles_by_driver AS
SELECT
    v.plate_number,
    v.chassis_number,
    v.engine_number,
    v.color,
    v.model,
    v.year,
    v.vehicle_type,
    v.make,
    v.ownership,
    v.license_number,
    CONCAT(d.first_name, ' ', d.last_name) AS owner_name
FROM vehicle v
JOIN driver d ON v.license_number = d.license_number;

-- View 3: Vehicles with expired registrations
CREATE VIEW view_expired_vehicles AS
SELECT
    vr.registration_number,
    vr.plate_number,
    v.chassis_number,
    v.engine_number,
    v.model,
    v.make,
    vr.registration_date,
    DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) AS expiration_date,
    vr.registration_status,
    d.license_number,
    CONCAT(d.first_name, ' ', d.last_name) AS owner_name
FROM vehicle_registration vr
JOIN vehicle v ON vr.plate_number  = v.plate_number
JOIN driver  d ON vr.license_number = d.license_number
WHERE DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) < CURDATE()
   OR vr.registration_status = 'expired';

-- View 4: Drivers with expired or suspended licenses
CREATE VIEW view_invalid_licenses AS
SELECT
    license_number,
    CONCAT(first_name, ' ', last_name) AS driver_name,
    license_type,
    license_status,
    date_of_birth,
    address
FROM driver
WHERE license_status IN ('expired', 'suspended');

-- View 5: Violations with driver name and parsed date
CREATE VIEW view_violations_by_driver AS
SELECT
    vt.violation_id,
    vt.license_number,
    CONCAT(d.first_name, ' ', d.last_name) AS driver_name,
    vt.apprehending_officer,
    vt.ticket_status,
    vt.total_fine_amount,
    vt.plate_number,
    vt.chassis_number,
    vt.engine_number,
    STR_TO_DATE(CONCAT(vt.year, '-', vt.month, '-', vt.day), '%Y-%M-%d') AS violation_date
FROM violation_ticket vt
JOIN driver d ON vt.license_number = d.license_number;

-- View 6: Violation counts grouped by type and year
CREATE VIEW view_violations_per_type_per_year AS
SELECT
    vt.year,
    vtht.violation_type,
    COUNT(*) AS total_violations
FROM violation_ticket vt
JOIN violation_ticket_has_type vtht ON vt.violation_id = vtht.violation_id
GROUP BY vt.year, vtht.violation_type;

-- View 7: Vehicles involved in violations (filter by address at query time)
CREATE VIEW view_vehicles_violations_by_location AS
SELECT DISTINCT
    v.plate_number,
    v.make,
    v.model,
    v.year,
    v.vehicle_type,
    v.color,
    d.license_number,
    CONCAT(d.first_name, ' ', d.last_name) AS owner_name,
    d.address
FROM vehicle v
JOIN driver           d  ON v.license_number  = d.license_number
JOIN violation_ticket vt ON vt.plate_number   = v.plate_number;