import sys
import db
from datetime import datetime

def print_row(row):
    if not row:
        print("No data.")
        return
    if isinstance(row, dict):
        items = [f"{k}={v}" for k, v in row.items()]
        print(", ".join(items))
    else:
        print(row)

def cmd_tables():
    tables = db.list_tables()
    if not tables:
        print("No tables found.")
    else:
        print("Tables:")
        for t in tables:
            print(" -", t)

def cmd_describe(parts):
    if len(parts) < 2:
        print("Usage: describe <table>")
        return
    table = parts[1]
    cols = db.get_table_columns(table)
    if not cols:
        print("Table not found or no columns.")
        return
    print(f"Columns in {table}:")
    for name, dtype, nullable in cols:
        print(f" - {name} : {dtype} (nullable={nullable})")
    pk = db.get_primary_key_column(table)
    print("Primary key:", pk)

def cmd_list(parts):
    if len(parts) < 2:
        print("Usage: list <table>")
        return
    table = parts[1]
    rows = db.list_rows(table, limit=200)
    if not rows:
        print("No rows.")
        return
    for r in rows:
        print_row(r)

def cmd_get(parts):
    if len(parts) < 3:
        print("Usage: get <table> <id>")
        return
    table = parts[1]
    id_arg = parts[2].strip()
    if not id_arg.isdigit():
        print("Error: id must be digits-only (for safety).")
        return
    pk_val = int(id_arg)
    row = db.get_row_by_pk(table, pk_val)
    if row:
        print_row(row)
    else:
        print("Not found or table has no primary key.")

def cmd_create(parts):
    if len(parts) < 2:
        print("Usage: create <table>")
        return
    table = parts[1]
    cols = db.get_table_columns(table)
    if not cols:
        print("Table not found or has no columns.")
        return

    data = {}
    print("Enter values for new row. Leave empty to insert NULL (if allowed).")
    for name, dtype, nullable in cols:
        if name.endswith("_id"):
            continue  

        val = input(f"  {name} ({dtype}) : ").strip()
        if val == "":
            data[name] = None
        else:
            if dtype in ('integer', 'bigint', 'smallint') and val.isdigit():
                data[name] = int(val)
            elif dtype == 'date':
                try:
                    data[name] = datetime.strptime(val, "%Y-%m-%d").date()
                except ValueError:
                    data[name] = val
            else:
                data[name] = val


    ok = db.create_row(table, data)
    if ok:
        print("Insert executed (ok).")
    else:
        print("Insert failed.")

def cmd_update(parts):
    if len(parts) < 3:
        print("Usage: update <table> <id>")
        return
    table = parts[1]
    id_arg = parts[2].strip()
    if not id_arg.isdigit():
        print("Error: id must be digits-only (for safety).")
        return
    pk_val = int(id_arg)
    row = db.get_row_by_pk(table, pk_val)
    if not row:
        print("Not found or table has no primary key.")
        return
    print("Current values:")
    print_row(row)

    cols = db.get_table_columns(table)
    new_data = {}
    print("Enter new values. Leave empty to keep current value.")
    for name, dtype, nullable in cols:
        cur_val = row.get(name)
        val = input(f"  {name} ({dtype}) [{cur_val}]: ").strip()
        if val == "":
            continue
        if dtype in ('integer','bigint','smallint') and val.isdigit():
            new_data[name] = int(val)
        else:
            if dtype == 'date':
                try:
                    new_data[name] = datetime.strptime(val, "%Y-%m-%d").date()
                except ValueError:
                    new_data[name] = val
            else:
                new_data[name] = val
    if not new_data:
        print("No changes provided.")
        return
    try:
        ok = db.update_row_by_pk(table, pk_val, new_data)
        if ok:
            print("Update successful.")
        else:
            print("Update failed.")
    except Exception as e:
        print("Update error:", e)

def cmd_delete(parts):
    if len(parts) < 3:
        print("Usage: delete <table> <id>")
        return
    table = parts[1]
    id_arg = parts[2].strip()
    if not id_arg.isdigit():
        print("Error: id must be digits-only (for safety).")
        return
    pk_val = int(id_arg)
    row = db.get_row_by_pk(table, pk_val)
    if not row:
        print("Not found or table has no primary key.")
        return
    print("About to delete:")
    print_row(row)
    c = input("Type 'yes' to confirm: ").strip().lower()
    if c != 'yes':
        print("Cancelled.")
        return
    try:
        ok = db.delete_row_by_pk(table, pk_val)
        if ok:
            print("Deleted.")
        else:
            print("Delete failed (maybe FK constraint).")
    except Exception as e:
        print("Delete error (likely FK constraint):", e)

def cmd_query(parts):
    if len(parts) < 2:
        print("Usage: query <table>")
        return
    table = parts[1]
    rows = db.complex_query_example(table)
    if not rows:
        print("No results or table doesn't have role/hired_on columns.")
        return
    for r in rows:
        print_row(r)

def main():
    print("Universal DB CLI. Type 'help' for commands.")
    while True:
        try:
            cmd = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            break
        if not cmd:
            continue
        parts = cmd.split()
        name = parts[0].lower()
        if name in ('help','h','?'):
            print("Commands: tables | describe <table> | list <table> | get <table> <id> | create <table> | update <table> <id> | delete <table> <id> | query <table> | exit")
        elif name == 'tables':
            cmd_tables()
        elif name == 'describe':
            cmd_describe(parts)
        elif name == 'list':
            cmd_list(parts)
        elif name == 'get':
            cmd_get(parts)
        elif name == 'create':
            cmd_create(parts)
        elif name == 'update':
            cmd_update(parts)
        elif name == 'delete':
            cmd_delete(parts)
        elif name == 'query':
            cmd_query(parts)
        elif name == 'exit':
            print("Bye.")
            break
        else:
            print("Unknown command. Type 'help'.")

if __name__ == "__main__":
    main()
