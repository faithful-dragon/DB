from typing import Any, Dict
from langgraph.graph import StateGraph, END
from Helper.logger_config import logger

from Nodes.IntentNode import intent_node
from Nodes.FetchSchemaNode import fetch_schema_node
from Nodes.GenerateSQLQueryNode import generate_sql_node
from Nodes.HumanApprovalNode import approval_node
from Nodes.ExecuteSQLQueryNode import execute_node
from Nodes.ParseResultNode import parse_result_node
from Helper.common import AgentState

graph = StateGraph(AgentState)

graph.add_node("intent", intent_node)
graph.add_node("fetch_schema", fetch_schema_node)
graph.add_node("generate_sql", generate_sql_node)
graph.add_node("approval", approval_node)
graph.add_node("execute", execute_node)
graph.add_node("parse_result", parse_result_node)

graph.set_entry_point("intent")
graph.add_edge("intent", "fetch_schema")
graph.add_edge("fetch_schema", "generate_sql")
graph.add_conditional_edges(
    "generate_sql",
    lambda s: "approval" if s["intent"] != "SELECT" else "execute",
    {"approval": "approval", "execute": "execute"},
)
graph.add_edge("approval", "execute")
graph.add_edge("execute", "parse_result")
graph.add_edge("parse_result", END)

agent = graph.compile()

# -----------------------------
# Interactive Loop
# -----------------------------
if __name__ == "__main__":
    print("Type 'exit' to quit.\n")
    while True:
        user_text = input("Ask something: ").strip()
        if user_text.lower() == "exit":
            print("👋 Exiting. Goodbye!")
            break

        # Invoke agent
        result = agent.invoke(
            {"user_input": user_text, "schema": None, "schema_update_required": False}
        )

        # Display final output
        print("\n✅ Final Response:")
        print(result["final_output"])
        print("\n" + "-"*50 + "\n")
