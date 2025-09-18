from Helper.common import AgentState
from Helper.logger_config import logger

def parse_result_node(state: AgentState) -> AgentState:
    logger.info("👉 Entering parse_result_node")
    result = state.get("result")
    state["final_output"] = {"query": state.get("sql_query"), "result": result}
    logger.info("✅ Final output prepared")
    return state