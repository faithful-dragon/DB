
from Helper.common import AgentState
from Helper.logger_config import logger

def approval_node(state: AgentState) -> AgentState:
    logger.info("👉 Entering approval_node")
    sql = state.get("sql_query", "")
    print(f"\n⚠️ Approval required for query:\n{sql}\n")
    approved = input("Approve? (y/n): ").strip().lower()
    state["approved"] = approved == "y"
    logger.info(f"✅ Approval: {state['approved']}")
    return state