# agent_main.py
from langgraph.graph import StateGraph, END
from Helper.logger_config import logger
from Helper.common import AgentState
from Nodes.FetchSchemaNode import fetch_schema_node
from Nodes.RefineUserQueryNode import refine_user_query_node
from Nodes.IntentNode import intent_node
from Nodes.GenerateSQLQueryNode import generate_sql_node
from Nodes.VerifySQLQueryNode import verify_sql_node
from Nodes.HumanApprovalNode import approval_node
from Nodes.ExecuteSQLQueryNode import execute_node
from Nodes.ParseResultNode import parse_result_node

graph = StateGraph(AgentState)
graph.add_node("fetch_schema", fetch_schema_node)
graph.add_node("refine_query", refine_user_query_node)
graph.add_node("intent", intent_node)
graph.add_node("generate_sql", generate_sql_node)
graph.add_node("verify_sql", verify_sql_node)
graph.add_node("approval", approval_node)
graph.add_node("execute", execute_node)
graph.add_node("parse_result", parse_result_node)
graph.set_entry_point("fetch_schema")
graph.add_edge("fetch_schema","refine_query")
graph.add_edge("refine_query","intent")
graph.add_edge("intent","generate_sql")
graph.add_edge("generate_sql","verify_sql")
graph.add_conditional_edges(
    "verify_sql",
    lambda s: (
        "approval" if s.get("verification_status") == "Pass" and s.get("intent") != "SELECT"
        else "execute" if s.get("verification_status") == "Pass" and s.get("intent") == "SELECT"
        else "parse_result" if s.get("verification_status") == "MaxFail"
        else "generate_sql"
    ),
    {"approval":"approval","execute":"execute","generate_sql":"generate_sql","parse_result":"parse_result"}
)
graph.add_edge("approval","execute")
graph.add_edge("execute","parse_result")
graph.add_edge("parse_result", END)
agent = graph.compile()

if __name__ == "__main__":
    persistent_state: AgentState = {
        "schema": None,
        "schema_update_required": False,
        "retries": 0,
        "retry_logs": [],
        "max_retries": 2,
    }

    print("Type 'exit' to quit.\n")
    while True:
        user_text = input("Ask something: ").strip()
        if user_text.lower() == "exit":
            break
        persistent_state["user_input"] = user_text
        result_state = agent.invoke(persistent_state)
        persistent_state.update(result_state)
        print("\n✅ Final Response:")
        print(result_state.get("result", "No output generated"))
        print("\n"+"-"*40+"\n")
