import json
from Helper.apiCall import Get_llm_response
from Prompts.GetSQLGeneratorPrompt import GetSQLGeneratorPrompt
from Helper.logger_config import logger
from Helper.common import AgentState

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
        state["sql_query"] = parsed.get("sql", "").strip()
        state["sql_reason"] = parsed.get("Reason", "").strip()

        # Optional: Warn if SQL is empty
        if not state["sql_query"] and state["intent"] != "OTHER":
            logger.warning("⚠️ LLM returned empty SQL for a valid intent. Please check prompt or input.")

    except Exception as e:
        state["sql_query"] = ""
        state["sql_reason"] = f"Failed to parse SQL from LLM response. Error: {e}"

    logger.info(f"✅ Generated SQL: {state['sql_query']} | Reason: {state['sql_reason']}")
    return state
