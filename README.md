# Staff CLI (PostgreSQL)

Beginner-friendly command-line app that connects to PostgreSQL and performs CRUD on the `staff` table.  
**All SQL is parameterized to prevent SQL injection.**  
Tested with Python 3.10+.

## Prerequisites
- Python 3.10+
- pip
- PostgreSQL 13+

## Environment variables
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS`  
You can also create a `.env` file with the same keys.

## Database setup
1) Run `ddl.sql` in your PostgreSQL.  
2) Run `seed.sql` to insert sample rows (≥10).

## Install and run
1) Install deps from `requirements.txt`.  
2) Start the app: `python app.py`.  
3) Type `help` for commands.
