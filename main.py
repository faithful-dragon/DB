import re
import json
from typing import Any, Dict
import dotenv

from db_util import get_schema, run_query
from Prompts.GetIntentPrompt import GetIntentPrompt
from Prompts.GetSQLGeneratorPrompt import GetSQLGeneratorPrompt
from langgraph.graph import StateGraph, END
from Helper.logger_config import logger
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from Helper.apiCall import Get_llm_response

# -----------------------------
# Load environment variables
# -----------------------------
dotenv.load_dotenv()

# -----------------------------
# Agent State
# -----------------------------
AgentState = Dict[str, Any]

# -----------------------------
# SQL Extractor
# -----------------------------
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

# -----------------------------
# Nodes
# -----------------------------
def intent_node(state: AgentState) -> AgentState:
    logger.info("👉 Entering intent_node")
    prompt_text = GetIntentPrompt()

    try:
        response_text = Get_llm_response(prompt_text, user_input=state["user_input"])
        parsed = json.loads(response_text)
        state["intent"] = parsed.get("intent", "OTHER").upper()
        state["Reason"] = parsed.get("Reason", "")
    except Exception as e:
        state["intent"] = "OTHER"
        state["Reason"] = f"Failed to parse LLM response. Error: {e}"

    logger.info(f"✅ Detected intent: {state['intent']} | Reason: {state['Reason']}")
    return state

def fetch_schema_node(state: AgentState) -> AgentState:
    logger.info("👉 Entering fetch_schema_node")
    if state.get("schema") is None or state.get("schema_update_required", False):
        schema = get_schema(schema_name="shop")
        state["schema"] = schema
        state["schema_update_required"] = False
        logger.info("✅ Schema fetched/updated")
    else:
        logger.info("✅ Schema already available")
    return state

def generate_sql_node(state: AgentState) -> AgentState:
    logger.info("👉 Entering generate_sql_node")
    prompt_text = GetSQLGeneratorPrompt()

    try:
        response_text = Get_llm_response(
            prompt_text,
            schema_name="shop",
            schema=state.get("schema"),
            user_input=state.get("user_input"),
            intent=state.get("intent")
        )
        parsed = json.loads(response_text)
        state["sql_query"] = parsed.get("sql", "")
        state["sql_reason"] = parsed.get("Reason", "")
    except Exception as e:
        state["sql_query"] = ""
        state["sql_reason"] = f"Failed to parse SQL from LLM response. Error: {e}"

    logger.info(f"✅ Generated SQL: {state['sql_query']} | Reason: {state['sql_reason']}")
    return state

def approval_node(state: AgentState) -> AgentState:
    logger.info("👉 Entering approval_node")
    sql = state.get("sql_query", "")
    print(f"\n⚠️ Approval required for query:\n{sql}\n")
    approved = input("Approve? (y/n): ").strip().lower()
    state["approved"] = approved == "y"
    logger.info(f"✅ Approval: {state['approved']}")
    return state

def execute_node(state: AgentState) -> AgentState:
    logger.info("👉 Entering execute_node")
    sql = state.get("sql_query")
    intent = state.get("intent")

    if intent == "SELECT":
        result = run_query(sql, commit=False)
    else:
        if state.get("approved"):
            result = run_query(sql, commit=True)
            state["schema_update_required"] = True
            logger.info("✅ Non-SELECT query executed, schema flagged for update")
        else:
            result = {"error": "Query not approved by human."}
            logger.warning("❌ Query execution skipped (not approved)")

    state["result"] = result
    return state

def parse_result_node(state: AgentState) -> AgentState:
    logger.info("👉 Entering parse_result_node")
    result = state.get("result")
    state["final_output"] = {"query": state.get("sql_query"), "result": result}
    logger.info("✅ Final output prepared")
    return state

# -----------------------------
# Build LangGraph
# -----------------------------
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
# Run Example
# -----------------------------
if __name__ == "__main__":
    user_text = input("Ask something: ")
    result = agent.invoke(
        {"user_input": user_text, "schema": None, "schema_update_required": False}
    )
    print("\n✅ Final Response:")
    print(result["final_output"])
