import re
from typing import Annotated, List, Any, TypedDict, Optional
import json
from Helper.logger_config import logger


class AgentState(TypedDict, total=False):
    user_input: Annotated[str, "static"]
    user_input_refined: str
    intent: str
    schema: str
    schema_update_required: bool
    sql_query: str
    sql_reason: str
    verification_status: str
    verification_feedback: str
    human_approval: str
    retries: int
    max_retries: int
    retry_logs: Annotated[List[str], "accumulate"]
    result: Optional[dict]
    error: str




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

def print_state(state: AgentState, title: str = "Agent State") -> None:
    """
    Pretty-print the AgentState dictionary with highlighting for empty/missing keys.

    Args:
        state (AgentState): Current agent state
        title (str): Optional title for logging
    """
    print("\n" + "="*60)
    print(f"{title}:")
    print("="*60)

    for key in [
        "user_input",
        "user_input_refined",
        "intent",
        "schema",
        "schema_update_required",
        "sql_query",
        "sql_reason",
        "verification_status",
        "verification_feedback",
        "human_approval",
        "retries",
        "max_retries",
        "retry_logs",
        "result"
    ]:
        value = state.get(key, None)
        if value in (None, "", []):
            print(f"{key}: ⚠️ EMPTY or MISSING")
        else:
            # Pretty-print JSON-like structures
            if isinstance(value, (dict, list)):
                print(f"{key}:\n{json.dumps(value, indent=4, ensure_ascii=False)}")
            else:
                print(f"{key}: {value}")

    print("="*60 + "\n")
