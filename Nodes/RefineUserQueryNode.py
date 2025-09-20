# Nodes/RefineUserQueryNode.py
import json
import re
from Helper.logger_config import logger
from Helper.common import AgentState
from Helper.apiCall import Get_llm_response
from Prompts.GetRefinedQueryPrompt import GetRefinedQueryPrompt

def refine_user_query_node(state: AgentState) -> AgentState:
    logger.info("Entering refine_user_query_node")
    logger.info(f"STATE ID at refine_user_query_node: {id(state)}")

    try:
        schema_json = json.dumps(state.get("schema", {}))

        response_text = Get_llm_response(
            GetRefinedQueryPrompt(),
            schema_name="shop",
            schema=schema_json,
            user_input=state.get("user_input"),
        )

        parsed = json.loads(response_text)
        refined_query = parsed.get("refined_query", "").strip()

        if refined_query:
            state["user_input_refined"] = refined_query
            logger.info(f"✅ Refined user query: {refined_query}")
        else:
            state["user_input_refined"] = state.get("user_input")
            logger.warning("⚠️ Refiner returned empty response, using original input.")

    except (json.JSONDecodeError, ValueError) as e:
        state["user_input_refined"] = state.get("user_input")
        logger.error(f"❌ Failed to parse JSON from refiner. Error: {e}. Raw: {response_text}")

    except Exception as e:
        state["user_input_refined"] = state.get("user_input")
        logger.error(f"❌ Unexpected error in refine_user_query_node: {e}")

    return state
