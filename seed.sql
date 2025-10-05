-- seed.sql — sample data (≥10 rows), adapted from a typical staff list
-- Note: we insert explicit IDs; then we fix the sequence.

INSERT INTO staff (staff_id, full_name, role, email, phone, hired_on) VALUES
(2,  'Alua',             'manager',        'alua@astanait.edu.kz',      '+7-702-000-2222', '2023-04-15'),
(3,  'Samat',            'senior_manager', 'samat@astanait.edu.kz',     '+7-705-000-3333', '2021-02-10'),
(5,  'Inkar',            'intern',         'inkar@astanait.edu.kz',     '+77771001001',    '2025-03-01'),
(6,  'Amina',            'intern',         'amina@astanait.edu.kz',     '+77771001002',    '2025-03-15'),
(1,  'Kristina',         'senior_intern',  'askar@gmail.com',           '+77011001111',    '2024-09-01'),
(4,  'Aidana Guide',     'intern',         'mansyr@astanait.edu.kz',    '+77771001000',    '2025-02-01'),
(8,  'Nurlan',           'intern',         'nurlan@example.com',        '+7-701-100-2000', '2025-01-10'),
(9,  'Zhanar',           'intern',         'zhanar@example.com',        '+7-701-100-2001', '2024-12-05'),
(10, 'Yerlan',           'manager',        'yerlan@example.com',        '+7-701-100-2002', '2022-09-01'),
(11, 'Dana',             'senior_intern',  'dana@example.com',          '+7-701-100-2003', '2024-11-11'),
(12, 'Timur',            'intern',         'timur@example.com',         '+7-701-100-2004', '2025-03-20');

-- Fix the staff_id sequence so future inserts work naturally
SELECT setval(pg_get_serial_sequence('staff', 'staff_id'),
              COALESCE((SELECT MAX(staff_id) FROM staff), 1), true);
