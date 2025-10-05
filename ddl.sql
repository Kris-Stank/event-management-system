-- ddl.sql — Database schema for the CLI app (PostgreSQL)

-- Drop table if you are re-running the DDL during testing (optional)
DROP TABLE IF EXISTS staff;

-- Main CRUD table
CREATE TABLE staff (
    staff_id    SERIAL PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    role        VARCHAR(50)  NOT NULL,
    email       VARCHAR(120) NOT NULL UNIQUE,
    phone       VARCHAR(25),
    hired_on    DATE NOT NULL,
    -- tiny data-quality checks (simple on purpose for a student project)
    CONSTRAINT chk_role CHECK (char_length(role) >= 3),
    CONSTRAINT chk_name CHECK (char_length(full_name) >= 2)
);

-- Helpful index for search/filter demos
CREATE INDEX idx_staff_role ON staff(role);
CREATE INDEX idx_staff_hired_on ON staff(hired_on);
