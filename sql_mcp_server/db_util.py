import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "Post321"),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "postgres"),
    )

def get_schema(schema_name: str = "shop"):
    """Fetch table and column info from the database schema."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = '{schema_name}'
        ORDER BY table_name, ordinal_position;
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    schema = {}
    for table, column, dtype in rows:
        schema.setdefault(table, []).append({"column": column, "type": dtype})
    return schema


def run_query(sql: str, commit: bool = False):
    """
    Execute a SQL query.
    SELECT returns structured rows.
    INSERT/UPDATE/DELETE return rowcount + status.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)

            if cur.description:  # SELECT → has column metadata
                rows = cur.fetchall()
                columns = [desc.name for desc in cur.description]
                return {"columns": columns, "rows": [list(r.values()) for r in rows]}

            if commit:
                conn.commit()
                return {"status": "success", "rowcount": cur.rowcount}
            else:
                return {"status": "success"}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        conn.close()
