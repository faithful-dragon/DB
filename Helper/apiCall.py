from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import dotenv
dotenv.load_dotenv()

# Initialize LLM (you can move it here or keep it global)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def Get_llm_response(prompt_template: str, **kwargs) -> str:
    """
    Generates a response from the LLM using a prompt template and keyword arguments.

    Args:
        prompt_template (str): The prompt template string.
        **kwargs: Variables to fill into the prompt template.

    Returns:
        str: The content of the LLM response.
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    response = llm.invoke(prompt.format_messages(**kwargs))
    return response.content.strip()
