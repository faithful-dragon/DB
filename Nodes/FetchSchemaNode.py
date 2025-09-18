import psycopg2
from Helper.logger_config import logger
from Helper.common import AgentState, print_schema
import db_util

def fetch_schema_node(state: AgentState) -> AgentState:
    """
    Fetches the database schema details directly using psycopg2 connection.
    Resolves USER-DEFINED types like enums to their supported values.
    """
    logger.info("👉 Entering fetch_schema_node")

    if state.get("schema") is None or state.get("schema_update_required", False):
        try:
            conn = db_util.get_connection()
            cur = conn.cursor()

            # Fetch table names
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='shop'
                  AND table_type='BASE TABLE';
            """)
            tables = [row[0] for row in cur.fetchall()]

            schema = {"stat": "Pass", "schema_name": "shop", "tables": []}

            for table in tables:
                # Fetch columns and data types
                cur.execute("""
                    SELECT column_name, data_type, udt_name
                    FROM information_schema.columns
                    WHERE table_name=%s;
                """, (table,))
                columns = cur.fetchall()

                column_names = []
                datatypes = {}

                for col_name, data_type, udt_name in columns:
                    column_names.append(col_name)
                    if data_type == "USER-DEFINED":
                        # Check if it's an enum
                        cur.execute("""
                            SELECT enumlabel
                            FROM pg_type t
                            JOIN pg_enum e ON t.oid = e.enumtypid
                            WHERE t.typname=%s;
                        """, (udt_name,))
                        enum_values = [row[0] for row in cur.fetchall()]
                        datatypes[col_name] = f"{udt_name} (enum: {enum_values})"
                    else:
                        datatypes[col_name] = data_type

                # Primary keys
                cur.execute("""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tco
                    JOIN information_schema.key_column_usage kcu 
                      ON kcu.constraint_name = tco.constraint_name
                      AND kcu.table_name = tco.table_name
                    WHERE tco.constraint_type = 'PRIMARY KEY'
                      AND kcu.table_name=%s;
                """, (table,))
                primary_key = [row[0] for row in cur.fetchall()]

                # Foreign keys
                cur.execute("""
                    SELECT
                        kcu.column_name, 
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY' AND kcu.table_name=%s;
                """, (table,))
                foreign_keys = [f"{row[0]} -> {row[1]}({row[2]})" for row in cur.fetchall()]

                # Sequences
                cur.execute(f"""
                    SELECT relname
                    FROM pg_class
                    WHERE relkind='S' AND relname LIKE '{table}_%';
                """)
                sequences = [row[0] for row in cur.fetchall()]

                # Table constraints
                cur.execute("""
                    SELECT constraint_name || ' ' || constraint_type
                    FROM information_schema.table_constraints
                    WHERE table_name=%s;
                """, (table,))
                constraints = [row[0] for row in cur.fetchall()]

                schema["tables"].append({
                    "name": table,
                    "column_names": column_names,
                    "datatypes": datatypes,
                    "primary_key": primary_key,
                    "foreign_keys": foreign_keys,
                    "sequences": sequences,
                    "constraints": constraints
                })

            cur.close()
            conn.close()

            state["schema"] = schema
            state["schema_update_required"] = False
            logger.info("✅ Schema fetched and stored in state")
            print_schema(schema)

        except Exception as e:
            logger.error(f"❌ Failed to fetch schema: {e}")
            state["schema"] = {"stat": "Fail", "details": str(e)}

    else:
        logger.info("✅ Schema already available in state")

    return state
