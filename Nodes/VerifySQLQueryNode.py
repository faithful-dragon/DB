from Helper.logger_config import logger
from Helper.apiCall import Get_llm_response
from Prompts.GetSQLVerificationPrompt import GetSQLVerificationPrompt
from Helper.common import AgentState, print_state
import json


def verify_sql_node(state: AgentState) -> AgentState:
    logger.info("Entering verify_sql_node")
    sql = state.get("sql_query", "").strip()
    schema_json = json.dumps(state.get("schema", {}))

    if not sql:
        state["verification_status"] = "Fail"
        state["verification_feedback"] = "No SQL generated. Please regenerate."
        logger.warning("❌ No SQL generated")
        return state

    try:
        # print_state(state)
        response_text = Get_llm_response(
            GetSQLVerificationPrompt(),
            schema_name="shop",
            schema=schema_json,
            sql_query=sql
        )

        logger.info(f"🤖 LLM verification response: {response_text}")
        parsed = json.loads(response_text)
        state["verification_status"] = parsed.get("verification_status", "Fail")
        state["verification_feedback"] = parsed.get("verification_feedback", "")

    except Exception as e:
        state["verification_status"] = "Fail"
        state["verification_feedback"] = f"LLM verification failed: {e}"
        logger.error(f"❌ SQL verification LLM call failed: {e}")

    return state
