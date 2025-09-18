import re
from typing import Dict, Any

AgentState = Dict[str, Any]

def extract_sql(text: str) -> str:
    """Extract the first SQL statement from LLM output."""
    match = re.search(r"```sql\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"(.*?;)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def print_schema(schema: dict):
    """
    Prints the database schema in a readable format, resolving enums.
    """
    if not schema or "tables" not in schema:
        print("No schema available to display.")
        return

    print(f"\nSchema: {schema.get('schema_name', 'Unknown')} (Status: {schema.get('stat', 'N/A')})\n")
    for table in schema["tables"]:
        print(f"Table: {table['name']}")
        print(f"  Columns:")
        for col in table["column_names"]:
            dtype = table["datatypes"].get(col, "unknown")
            print(f"    - {col}: {dtype}")
        print(f"  Primary Key: {table['primary_key'] or 'None'}")
        print(f"  Foreign Keys: {table['foreign_keys'] or 'None'}")
        print(f"  Sequences: {table['sequences'] or 'None'}")
        print(f"  Constraints: {table['constraints'] or 'None'}")
        print("-" * 50)
