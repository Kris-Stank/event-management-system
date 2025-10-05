

import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
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


# -----------------------
# Метаданные / помощь
# -----------------------
def list_tables():
    sql_text = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_text)
            rows = [r[0] for r in cur.fetchall()]
            return rows


def get_table_columns(table):
    sql_text = sql.SQL("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position;
    """)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_text, (table,))
            return cur.fetchall()


def get_primary_key_column(table):
    sql_text = """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON kcu.constraint_name = tc.constraint_name
         AND kcu.constraint_schema = tc.constraint_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = 'public'
          AND tc.table_name = %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_text, (table,))
            row = cur.fetchone()
            return row[0] if row else None


# -----------------------
# CRUD для любой таблицы
# -----------------------
def list_rows(table, limit=100):
    q = sql.SQL("SELECT * FROM {tbl} ORDER BY 1 LIMIT %s").format(
        tbl=sql.Identifier(table)
    )
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(q, (limit,))
            return cur.fetchall()


def get_row_by_pk(table, pk_value):
    pk_col = get_primary_key_column(table)
    if not pk_col:
        return None  # нет первичного ключа
    q = sql.SQL("SELECT * FROM {tbl} WHERE {pk} = %s").format(
        tbl=sql.Identifier(table),
        pk=sql.Identifier(pk_col)
    )
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(q, (pk_value,))
            return cur.fetchone()


def create_row(table, data: dict):
    if not data:
        raise ValueError("No data provided")

    cols = [sql.Identifier(c) for c in data.keys()]
    vals_placeholders = sql.SQL(", ").join(sql.Placeholder() * len(data))
    cols_sql = sql.SQL(", ").join(cols)

    insert = sql.SQL("INSERT INTO {tbl} ({cols}) VALUES ({vals})").format(
        tbl=sql.Identifier(table),
        cols=cols_sql,
        vals=vals_placeholders
    )

    params = tuple(data.values())

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(insert, params)
            # Попытка вернуть вставленную строку по PK, если есть PK и он был сгенерирован.
            pk_col = get_primary_key_column(table)
            if pk_col:
                # Если PK — serial, можно попытаться получить lastval, но это ненадёжно для общей таблицы.
                # Поэтому просто попытаемся найти по сочетанию уникальных полей — но для простоты вернём True.
                conn.commit()
                return True
            conn.commit()
            return True


def update_row_by_pk(table, pk_value, new_data: dict):
    pk_col = get_primary_key_column(table)
    if not pk_col:
        return False

    if not new_data:
        return False

    set_parts = []
    params = []
    for k, v in new_data.items():
        set_parts.append(sql.SQL("{col} = %s").format(col=sql.Identifier(k)))
        params.append(v)
    params.append(pk_value)

    q = sql.SQL("UPDATE {tbl} SET {sets} WHERE {pk} = %s").format(
        tbl=sql.Identifier(table),
        sets=sql.SQL(", ").join(set_parts),
        pk=sql.Identifier(pk_col)
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(q, tuple(params))
            updated = cur.rowcount
            conn.commit()
            return updated > 0


def delete_row_by_pk(table, pk_value):
    pk_col = get_primary_key_column(table)
    if not pk_col:
        return False

    q = sql.SQL("DELETE FROM {tbl} WHERE {pk} = %s").format(
        tbl=sql.Identifier(table),
        pk=sql.Identifier(pk_col)
    )
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(q, (pk_value,))
                deleted = cur.rowcount
                conn.commit()
                return deleted > 0
            except psycopg2.Error as e:
                conn.rollback()
                # Пробрасываем исключение дальше, чтобы интерфейс мог показать сообщение
                raise


# -----------------------
# Пример сложного запроса (можно оставить по-табличному)
# -----------------------
def complex_query_example(table):
    cols = [c[0] for c in get_table_columns(table)]
    if 'role' not in cols or 'hired_on' not in cols:
        return []

    q = sql.SQL("""
        SELECT * FROM {tbl}
        WHERE (role = 'intern' AND hired_on >= DATE '2024-01-01')
           OR (role ILIKE '%manager%' AND hired_on < DATE '2023-01-01')
        ORDER BY hired_on DESC
        LIMIT 200
    """).format(tbl=sql.Identifier(table))

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(q)
            return cur.fetchall()
