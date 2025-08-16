from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from ...core.database import engine
from ...core.config import OPENAI_API_KEY

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0, openai_api_key=OPENAI_API_KEY)

# Connect LangChain to the database
# LangChain will use this to inspect table schemas and execute queries.
db = SQLDatabase(engine=engine)

# Create the SQL Agent
# This agent is a specialized chain that knows how to interact with SQL databases.
sql_agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    agent_type="openai-tools",
    verbose=True, # Set to True to see the agent's thought process
    prompt_suffix="Only use the regulation table to answer questions."
)

def query_database(user_question: str) -> str:
    """
    Uses the SQL Agent to query the regulation database based on a user's question.
    """
    try:
        response = sql_agent_executor.invoke({
            "input": f"Answer the following user's question: {user_question}"
        })
        return response.get("output", "I could not retrieve an answer from the database.")
    except Exception as e:
        # Handle potential errors during query execution
        return f"An error occurred: {e}"