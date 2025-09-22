
from Helper.common import AgentState
from Helper.logger_config import logger

def approval_node(state: AgentState) -> AgentState:
    logger.info("Entering approval_node")
    logger.info(f"STATE ID at approval_node: {id(state)}")
    sql = state.get("sql_query", "")
    print(f"\n⚠️ Approval required for query:\n{sql}\n")
    approved = input("Approve? (y/n): ").strip().lower()
    state["human_approval"] = approved == "y"
    logger.info(f"✅ Approval: {state['human_approval']}")
    return state