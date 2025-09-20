from Helper.logger_config import logger
from Helper.apiCall import Get_llm_response
from Prompts.GetIntentPrompt import GetIntentPrompt
from Helper.common import AgentState
import json

def intent_node(state: AgentState) -> AgentState:
    logger.info("Entering intent_node")
    logger.info(f"STATE ID at intent_node: {id(state)}")
    prompt_text = GetIntentPrompt()

    try:
        response_text = Get_llm_response(prompt_text, user_input=state["user_input_refined"])
        parsed = json.loads(response_text)
        state["intent"] = parsed.get("intent", "OTHER").upper()
        state["Reason"] = parsed.get("Reason", "")
    except Exception as e:
        state["intent"] = "OTHER"
        state["Reason"] = f"Failed to parse LLM response. Error: {e}"

    logger.info(f"✅ Detected intent: {state['intent']} | Reason: {state['Reason']}")
    return state