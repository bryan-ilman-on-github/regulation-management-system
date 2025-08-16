from ...core.database import engine
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

# Initialize global variables to None, they will be populated on first use
_llm = None
_db = None
_sql_agent_executor = None


def get_sql_agent():
    """
    Lazily initializes and returns a single instance of the SQL agent executor.
    The database connection and LLM are only created on the first call.
    """
    global _llm, _db, _sql_agent_executor

    # This check ensures that the setup runs only once
    if _sql_agent_executor is None:
        # Configuration is imported and used here to avoid load-time errors
        from ...core.config import OPENAI_API_KEY

        # Initialize the LLM
        _llm = ChatOpenAI(
            model="gpt-4-turbo-preview", temperature=0, openai_api_key=OPENAI_API_KEY
        )

        # Connect LangChain to the database
        _db = SQLDatabase(engine=engine)

        # Create the SQL Agent
        _sql_agent_executor = create_sql_agent(
            llm=_llm,
            db=_db,
            agent_type="openai-tools",
            verbose=True,
            prompt_suffix="Only use the regulation table to answer questions.",
        )

    return _sql_agent_executor


def query_database(user_question: str) -> str:
    """
    Uses the SQL Agent to query the regulation database based on a user's question.
    """
    try:
        # Get the agent instance (it will be created if it doesn't exist yet)
        agent = get_sql_agent()

        response = agent.invoke(
            {"input": f"Answer the following user's question: {user_question}"}
        )
        return response.get(
            "output", "I could not retrieve an answer from the database."
        )
    except Exception as e:
        # Handle potential errors during query execution
        return f"An error occurred: {e}"
