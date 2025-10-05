"""
app.py — Simple CLI app for CRUD on 'staff' table.
All DB work is in db.py. This file just handles user I/O.

Commands:
  create            -> add a staff record
  list              -> list all staff
  get <id>          -> get a staff by id
  update <id>       -> update a staff by id (press Enter to keep a field)
  delete <id>       -> delete a staff by id (asks to confirm)
  query             -> run the prepared complex SELECT
  exit              -> quit
"""

from datetime import datetime
import db  # our helper module

def print_row(row):
    """Pretty-print one staff row."""
    if not row:
        print("No data.")
        return
    print(f"[{row['staff_id']}] {row['full_name']} | {row['role']} | {row['email']} | {row['phone']} | {row['hired_on']}")

def cmd_create():
    print("Create new staff record:")
    full_name = input("  Enter full name (required): ").strip()
    role = input("  Enter role (e.g., intern/manager): ").strip()
    email = input("  Enter email: ").strip()
    phone = input("  Enter phone: ").strip()
    hired_on_str = input("  Enter hired_on (YYYY-MM-DD): ").strip()

    if not full_name or not role or not email or not hired_on_str:
        print("Error: full_name, role, email, hired_on are required.")
        return

    try:
        hired_on = datetime.strptime(hired_on_str, "%Y-%m-%d").date()
    except ValueError:
        print("Error: hired_on must be in format YYYY-MM-DD.")
        return

    try:
        new_row = db.create_staff(full_name, role, email, phone, hired_on)
        print("Created:")
        print_row(new_row)
    except Exception as e:
        print("Create failed:", e)

def cmd_list():
    rows = db.list_staff()
    if not rows:
        print("No staff yet.")
    else:
        for r in rows:
            print_row(r)

def cmd_get(parts):
    if len(parts) < 2:
        print("Usage: get <id>")
        return
    try:
        staff_id = int(parts[1])
    except ValueError:
        print("Error: id must be an integer (injection attempts will not work here).")
        return
    row = db.get_staff(staff_id)
    if row:
        print_row(row)
    else:
        print("Not found.")

def cmd_update(parts):
    if len(parts) < 2:
        print("Usage: update <id>")
        return
    try:
        staff_id = int(parts[1])
    except ValueError:
        print("Error: id must be an integer.")
        return

    current = db.get_staff(staff_id)
    if not current:
        print("Record not found.")
        return

    print("Current values (press Enter to keep):")
    print_row(current)

    full_name = input(f"  full_name [{current['full_name']}]: ").strip()
    role = input(f"  role [{current['role']}]: ").strip()
    email = input(f"  email [{current['email']}]: ").strip()
    phone = input(f"  phone [{current['phone']}]: ").strip()
    hired_on_str = input(f"  hired_on [{current['hired_on']} in YYYY-MM-DD]: ").strip()

    hired_on = None
    if hired_on_str:
        try:
            hired_on = datetime.strptime(hired_on_str, "%Y-%m-%d").date()
        except ValueError:
            print("Error: hired_on must be in format YYYY-MM-DD.")
            return

    try:
        updated = db.update_staff(
            staff_id,
            full_name if full_name else None,
            role if role else None,
            email if email else None,
            phone if phone else None,
            hired_on
        )
        if updated:
            print("Updated:")
            print_row(updated)
        else:
            print("Update failed: not found.")
    except Exception as e:
        print("Update failed:", e)

def cmd_delete(parts):
    if len(parts) < 2:
        print("Usage: delete <id>")
        return
    try:
        staff_id = int(parts[1])
    except ValueError:
        print("Error: id must be an integer.")
        return

    row = db.get_staff(staff_id)
    if not row:
        print("Record not found.")
        return

    print("You are about to delete:")
    print_row(row)
    confirm = input("Type 'yes' to confirm: ").strip().lower()
    if confirm != "yes":
        print("Delete cancelled.")
        return

    try:
        deleted = db.delete_staff(staff_id)
        if deleted:
            print("Deleted:")
            print_row(deleted)
        else:
            print("Delete failed: not found.")
    except Exception as e:
        print("Delete failed:", e)

def cmd_query():
    rows = db.complex_query()
    print("Complex query results:")
    for r in rows:
        print(f"[{r['staff_id']}] {r['full_name']} | {r['role']} | {r['email']} | {r['hired_on']}")

def main():
    print("Staff CLI (PostgreSQL). Type 'help' for commands.")
    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not cmd:
            continue

        parts = cmd.split()
        name = parts[0].lower()

        if name == "help":
            print("Commands: create | list | get <id> | update <id> | delete <id> | query | exit")
        elif name == "create":
            cmd_create()
        elif name == "list":
            cmd_list()
        elif name == "get":
            cmd_get(parts)
        elif name == "update":
            cmd_update(parts)
        elif name == "delete":
            cmd_delete(parts)
        elif name == "query":
            cmd_query()
        elif name == "exit":
            print("Bye.")
            break
        else:
            print("Unknown command. Type 'help'.")

if __name__ == "__main__":
    main()
