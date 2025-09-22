import json
from Helper.logger_config import logger
from Helper.common import AgentState
from Helper.apiCall import Get_llm_response
from Prompts.GetSQLGeneratorPrompt import GetSQLGeneratorPrompt

def generate_sql_node(state: AgentState) -> AgentState:
    logger.info("Entering generate_sql_node")
    logger.info(f"STATE ID at generate_sql_node: {id(state)}")

    feedback = state.get("verification_feedback", "")

    try:
        # Convert schema dict to JSON string for safe injection into prompt
        schema_json = json.dumps(state.get("schema", {}))

        # Call LLM and pass parameters
        response_text = Get_llm_response(
            GetSQLGeneratorPrompt(),
            schema_name="shop",
            schema=schema_json,
            user_input=state.get("user_input_refined"),
            intent=state.get("intent"),
            verification_feedback=feedback
        )

        # Ensure valid JSON
        parsed = json.loads(response_text)
        state["sql_query"] = parsed.get("sql", "").strip()
        state["sql_reason"] = parsed.get("Reason", "").strip()

        if not state["sql_query"] and state.get("intent") != "OTHER":
            logger.warning("⚠️ LLM returned empty SQL for a valid intent. Please check prompt or input.")

    except json.JSONDecodeError as e:
        state["sql_query"] = ""
        state["sql_reason"] = f"Failed to parse JSON from LLM response. Error: {e}. Raw response: {response_text}"
        logger.error(f"❌ SQL generation failed: {state['sql_reason']}")

    except Exception as e:
        state["sql_query"] = ""
        state["sql_reason"] = f"Unexpected error: {e}"
        logger.error(f"❌ SQL generation failed: {state['sql_reason']}")

    logger.info(f"✅ Generated SQL: {state['sql_query']} | Reason: {state['sql_reason']}")
    return state
