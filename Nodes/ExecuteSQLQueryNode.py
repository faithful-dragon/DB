from Helper.common import AgentState
from db_util import run_query
from Helper.logger_config import logger


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