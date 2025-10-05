"""
db.py — Database helper functions for the CLI app.

Simple, beginner-style code with clear comments.
Uses environment variables for connection details.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load .env (optional, but helpful for local dev)
load_dotenv()

def get_connection():
    """
    Create a database connection using env vars.
    Returns a psycopg2 connection. Exits with a helpful message if failed.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", "")
        )
        return conn
    except Exception as e:
        print("Error: cannot connect to the database. Check env vars and Postgres is running.")
        print("Detailed message:", e)
        sys.exit(1)


def create_staff(full_name, role, email, phone, hired_on):
    """Insert a new staff row. Returns newly created row as dict."""
    sql = """
        INSERT INTO staff (full_name, role, email, phone, hired_on)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING staff_id, full_name, role, email, phone, hired_on;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (full_name, role, email, phone, hired_on))
            row = cur.fetchone()
            conn.commit()
            return row


def list_staff():
    """Return all staff rows ordered by staff_id."""
    sql = """
        SELECT staff_id, full_name, role, email, phone, hired_on
        FROM staff
        ORDER BY staff_id;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return rows


def get_staff(staff_id):
    """Return one staff row by id, or None if not found."""
    sql = """
        SELECT staff_id, full_name, role, email, phone, hired_on
        FROM staff
        WHERE staff_id = %s;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (staff_id,))
            row = cur.fetchone()
            return row


def update_staff(staff_id, full_name=None, role=None, email=None, phone=None, hired_on=None):
    """
    Update fields if the user provided new values; keep existing if None.
    Returns updated row or None if not found.
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get current values first
            cur.execute("""
                SELECT staff_id, full_name, role, email, phone, hired_on
                FROM staff WHERE staff_id = %s;
            """, (staff_id,))
            current = cur.fetchone()
            if not current:
                return None

            # Use new value if provided, otherwise keep the old one
            new_full_name = full_name if full_name else current["full_name"]
            new_role = role if role else current["role"]
            new_email = email if email else current["email"]
            new_phone = phone if phone else current["phone"]
            new_hired_on = hired_on if hired_on else current["hired_on"]

            cur.execute("""
                UPDATE staff
                SET full_name = %s,
                    role = %s,
                    email = %s,
                    phone = %s,
                    hired_on = %s
                WHERE staff_id = %s
                RETURNING staff_id, full_name, role, email, phone, hired_on;
            """, (new_full_name, new_role, new_email, new_phone, new_hired_on, staff_id))
            updated = cur.fetchone()
            conn.commit()
            return updated


def delete_staff(staff_id):
    """Delete a row by id. Returns the deleted row (for evidence) or None if not found."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # fetch first (for evidence screenshot)
            cur.execute("""
                SELECT staff_id, full_name, role, email, phone, hired_on
                FROM staff WHERE staff_id = %s;
            """, (staff_id,))
            row = cur.fetchone()
            if not row:
                return None

            cur.execute("DELETE FROM staff WHERE staff_id = %s;", (staff_id,))
            conn.commit()
            return row


def complex_query():
    """
    Example complex SELECT with AND/OR.
    Matches the assignment’s requirement.
    """
    sql = """
        SELECT staff_id, full_name, role, email, hired_on
        FROM staff
        WHERE (role = 'intern' AND hired_on >= DATE '2024-01-01')
           OR (role ILIKE '%manager%' AND hired_on < DATE '2023-01-01')
        ORDER BY hired_on DESC;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return rows
