from Helper.common import AgentState
from Helper.logger_config import logger

def parse_result_node(state: AgentState) -> AgentState:
    logger.info("Entering parse_result_node")
    logger.info(f"STATE ID at parse_result_node: {id(state)}")

    result = state.get("result", "")
    # print(f"\n⚠️ Parsing result:\n{result}\n")

    query = state.get("sql_query")

    if result is None:
        output = {
            "query": query,
            "columns": [],
            "rows": []
        }
    elif isinstance(result, dict) and "error" in result:
        output = {
            "query": query,
            "columns": ["error"],
            "rows": [[result["error"]]]
        }
    elif isinstance(result, dict) and "rows" in result and "columns" in result:
        # ✅ Standard SELECT result
        output = {
            "query": query,
            "columns": result.get("columns", []),
            "rows": result.get("rows", [])
        }
    else:
        # ✅ Non-SELECT (INSERT/UPDATE/DELETE) result
        output = {
            "query": query,
            "columns": ["result"],
            "rows": [[str(result)]]
        }

    state["result"] = output
    logger.info(f"✅ Final output prepared: {output}")
    return state
