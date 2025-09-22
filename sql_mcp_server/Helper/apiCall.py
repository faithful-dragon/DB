from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import dotenv
from Helper.logger_config import logger
dotenv.load_dotenv()

# Initialize LLM (you can move it here or keep it global)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# def Get_llm_response(prompt_template: str, **kwargs) -> str: 
   #""" Generates a response from the LLM using a prompt template and keyword arguments. Args: prompt_template (str): The prompt template string. **kwargs: Variables to fill into the prompt template. Returns: str: The content of the LLM response. """ prompt = ChatPromptTemplate.from_template(prompt_template) logger.info("🤖 LLM call") # print(prompt.format_messages(**kwargs)) response = llm.invoke(prompt.format_messages(**kwargs)) # logger.info(f"🤖 LLM response: {response.content.strip()}") return response.content.strip()

def Get_llm_response2(prompt_template: str, **kwargs) -> str:
    """
    Generates a response from the LLM using a prompt template and keyword arguments.
    Handles errors gracefully and returns a safe string.

    Args:
        prompt_template (str): The prompt template string.
        **kwargs: Variables to fill into the prompt template.

    Returns:
        str: The content of the LLM response, or an error message.
    """
    try:
        # Fill variables into the prompt
        prompt = ChatPromptTemplate.from_template(prompt_template)
        logger.info("🤖 LLM call")

        # Format messages for the LLM
        messages = prompt.format_messages(**kwargs)

        # Invoke the LLM
        response = llm.invoke(messages)

        # Extract and clean content
        content = response.content.strip()

        # Remove any surrounding code blocks (```json ... ```), if present
        if content.startswith("```") and content.endswith("```"):
            content = "\n".join(content.splitlines()[1:-1]).strip()

        logger.info(f"🤖 LLM response: {content}")
        return content

    except KeyError as ke:
        logger.error(f"❌ LLM formatting failed, missing key: {ke}")
        return f'Error: Missing key {ke} in prompt variables.'
    except AttributeError as ae:
        logger.error(f"❌ LLM response handling failed: {ae}")
        return f'Error: Invalid LLM response object ({ae}).'
    except Exception as e:
        logger.error(f"❌ LLM call failed: {e}")
        return f'Error: {e}'


from langchain_google_genai import ChatGoogleGenerativeAI
import re
gemini_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

def Get_llm_response(prompt_template: str, **kwargs) -> str:
    """
    Generates a response from Gemini LLM using a prompt template and keyword arguments.
    Automatically cleans up backticks or markdown wrapping.

    Args:
        prompt_template (str): The prompt template string.
        **kwargs: Variables to fill into the prompt template.

    Returns:
        str: The cleaned content of the LLM response.
    """
    try:
        # Fill variables into the prompt
        prompt = ChatPromptTemplate.from_template(prompt_template)
        logger.info("🤖 Gemini LLM call")
        
        # Invoke the Gemini model
        response = gemini_llm.invoke(prompt.format_messages(**kwargs))
        content = response.content.strip()
        
        # Remove ``` or ```json wrapping if present
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        
        logger.info(f"🤖 Gemini LLM response: {content}")
        return content

    except Exception as e:
        logger.error(f"❌ Gemini LLM call failed: {e}")
        return f"Error: {e}"