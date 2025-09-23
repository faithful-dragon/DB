# main.py
from langgraph.graph import StateGraph, END
from Helper.logger_config import logger
from Nodes.IntentNode import intent_node
from Nodes.FetchSchemaNode import fetch_schema_node
from Nodes.GenerateSQLQueryNode import generate_sql_node
from Nodes.HumanApprovalNode import approval_node
from Nodes.ExecuteSQLQueryNode import execute_node
from Nodes.ParseResultNode import parse_result_node
from Nodes.VerifySQLQueryNode import verify_sql_node
from Nodes.RefineUserQueryNode import refine_user_query_node
from Nodes.RetryGenSQLNode import retry_generate_sql_node
from Helper.common import AgentState


# Initialize graph with state definition
graph = StateGraph(AgentState)

# Register nodes
graph.add_node("fetch_schema", fetch_schema_node)
graph.add_node("refine_query", refine_user_query_node)
graph.add_node("intent", intent_node)
graph.add_node("generate_sql", generate_sql_node)
graph.add_node("verify_sql", verify_sql_node)
graph.add_node("approval", approval_node)
graph.add_node("execute", execute_node)
graph.add_node("retry_generate_sql", retry_generate_sql_node)
graph.add_node("parse_result", parse_result_node)

# Define entry
graph.set_entry_point("fetch_schema")

# Define edges
graph.add_edge("fetch_schema", "refine_query")
graph.add_edge("refine_query", "intent")
graph.add_edge("intent", "generate_sql")
graph.add_edge("generate_sql", "verify_sql")

graph.add_conditional_edges(
    "verify_sql",
    lambda s: (
        "approval" if s["verification_status"] == "Pass" and s["intent"] != "SELECT"
        else "execute" if s["verification_status"] == "Pass" and s["intent"] == "SELECT"
        else "parse_result" if s["verification_status"] == "MaxFail"
        else "generate_sql"
    ),
    {
        "approval": "approval",
        "execute": "execute",
        "generate_sql": "generate_sql",
        "parse_result": "parse_result",
    },
)

graph.add_edge("approval", "execute")
graph.add_conditional_edges(
    "execute",
    lambda s: (
        "parse_result" if not s.get("result", {}).get("error")
        else "retry_generate_sql"
    ),
    {
        "retry_generate_sql": "retry_generate_sql",
        "parse_result": "parse_result",
    },
)
graph.add_edge("retry_generate_sql", "generate_sql")
graph.add_edge("parse_result", END)

# Compile agent
agent = graph.compile()


if __name__ == "__main__":
    print("Type 'exit' to quit.\n")

    # Persistent state for the session
    persistent_state: AgentState = {
        "schema": None,
        "schema_update_required": False,
        "retries": 0,
        "retry_logs": [],
        "max_retries": 2,
    }

    while True:
        user_text = input("Ask something: ").strip()
        if user_text.lower() == "exit":
            print("👋 Exiting. Goodbye!")
            break

        # Update only the user_input in persistent state
        persistent_state["user_input"] = user_text

        # Run agent with persistent state
        result_state = agent.invoke(persistent_state)

        # After execution, the persistent_state keeps updated schema
        # If you want, you can update the persistent_state itself with new fields
        persistent_state.update(result_state)

        # Extract final result
        result = getattr(result_state, "result", None)
        if isinstance(result_state, dict):
            result = result_state.get("result", None)

        print("\n✅ Final Response:")

        if not result:
            print("No output generated")
        else:
            query = result.get("query")
            columns = result.get("columns")
            rows = result.get("rows")
            error = result.get("error")
            result_msg = result.get("result")

            if query:
                print(f"\nQUERY:\n{query}\n")
            if columns:
                print(f"COLUMNS:\n{columns}\n")
            if error:
                print(f"ERROR:\n{error}\n")
            if rows:
                print("ROWS:")
                for row in rows:
                    print(row)
                print()
            elif result_msg:
                print(f"RESULT:\n{result_msg}\n")

        print("\n" + "-" * 50 + "\n")
