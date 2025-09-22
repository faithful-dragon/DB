# Helper/common.py
from typing import Annotated, List, Any, TypedDict, Optional
import json
import re
from Helper.logger_config import logger

class AgentState(TypedDict, total=False):
    user_input: Annotated[str, "static"]
    user_input_refined: str
    intent: str
    schema: Any
    schema_update_required: bool
    sql_query: str
    sql_reason: str
    verification_status: str
    verification_feedback: str
    human_approval: bool
    retries: int
    max_retries: int
    retry_logs: Annotated[List[str], "accumulate"]
    result: Optional[dict]
    error: str

def extract_sql(text: str) -> str:
    match = re.search(r"```sql\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"```(?:json)?\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"(.*?;)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def print_schema(schema: dict):
    if not schema or "tables" not in schema:
        print("No schema available to display.")
        return
    print(f"\nSchema: {schema.get('schema_name', 'Unknown')} (Status: {schema.get('stat', 'N/A')})\n")
    for table in schema["tables"]:
        print(f"Table: {table['name']}")
        print("  Columns:")
        for col in table["column_names"]:
            dtype = table["datatypes"].get(col, "unknown")
            print(f"    - {col}: {dtype}")
        print(f"  Primary Key: {table.get('primary_key') or 'None'}")
        print(f"  Foreign Keys: {table.get('foreign_keys') or 'None'}")
        print("-" * 40)

def print_state(state: AgentState, title: str = "Agent State") -> None:
    print("\n" + "="*60)
    print(f"{title}:")
    print("="*60)
    keys = [
        "user_input","user_input_refined","intent","schema","schema_update_required",
        "sql_query","sql_reason","verification_status","verification_feedback",
        "human_approval","retries","max_retries","retry_logs","result"
    ]
    for key in keys:
        val = state.get(key, None)
        if val in (None, "", []):
            print(f"{key}: ⚠️ EMPTY or MISSING")
        else:
            if isinstance(val, (dict, list)):
                print(f"{key}:\n{json.dumps(val, indent=4, ensure_ascii=False)}")
            else:
                print(f"{key}: {val}")
    print("="*60 + "\n")
