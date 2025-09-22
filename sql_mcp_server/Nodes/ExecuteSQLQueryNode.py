from Helper.common import AgentState
from db_util import run_query
from Helper.logger_config import logger

def execute_node(state: AgentState) -> AgentState:
    logger.info("Entering execute_node")
    logger.info(f"STATE ID at execute_node: {id(state)}")

    sql = state.get("sql_query")
    intent = state.get("intent")

    if not sql:
        logger.warning("❌ No SQL to execute")
        state["result"] = {"error": "No SQL query provided."}
        return state

    try:
        if intent == "SELECT":
            result = run_query(sql, commit=False)
            logger.info(f"✅ SELECT query executed, {len(result) if hasattr(result, '__len__') else 'unknown'} rows returned")
        else:
            if state.get("human_approval"):
                result = run_query(sql, commit=True)
                state["schema_update_required"] = True
                logger.info("✅ Non-SELECT query executed, schema flagged for update")
            else:
                result = {"error": "Query not approved by human."}
                logger.warning("❌ Query execution skipped (not approved)")
    except Exception as e:
        result = {"error": str(e)}
        logger.error(f"❌ Query execution failed: {e}")

    # Always log what is stored in state
    # logger.info(f"Storing result in state: {result}")
    state["result"] = result
    return state
