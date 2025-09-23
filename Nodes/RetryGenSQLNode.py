from Helper.common import AgentState
from Helper.logger_config import logger

def retry_generate_sql_node(state: AgentState) -> AgentState:
    """
    If SQL execution fails, pass error + retry info to generate_sql_node
    """
    logger.info("Entering retry_generate_sql_node")
    logger.info(f"STATE ID: {id(state)}")

    # Check if we have retries left
    retries = state.get("retries", 0)
    max_retries = state.get("max_retries", 2)

    # Extract error from execution
    error_msg = state.get("result", {}).get("error", None)

    if not error_msg:
        logger.info("No execution error detected, skipping retry.")
        return state  # Nothing to do

    if retries >= max_retries:
        logger.warning(f"Max retries reached ({retries}/{max_retries}), not regenerating SQL.")
        return state

    # Increment retry counter
    state["retries"] = retries + 1
    state["retry_logs"] = state.get("retry_logs", [])
    state["retry_logs"].append(error_msg)

    # Pass info back to generate_sql_node
    state["verification_feedback"] = (
        f"Previous SQL failed with error: {error_msg}. "
        f"Retry {state['retries']} of {max_retries}."
    )

    logger.info(f"Retrying generate_sql_node due to error: {error_msg}")
    return state
