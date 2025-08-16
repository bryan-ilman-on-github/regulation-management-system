from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool

from ..core.config import OPENAI_API_KEY
from .tools.sql_tool import query_database

# Initialize the master LLM
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name="gpt-4-turbo-preview", temperature=0)

# Define the tools the agent can use
tools = [
    Tool(
        name="RegulationDatabase",
        func=query_database,
        description="""Use this tool to answer questions about Indonesian regulations.
        This includes counting regulations, listing them by year, finding status,
        or any other question that can be answered by querying a SQL table
        named 'regulation'.""",
    )
]

# Create the prompt for the master agent
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a powerful assistant that can answer questions about Indonesian regulations."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create the master agent
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def get_intelligent_response(user_input: str) -> str:
    """
    Invokes the master agent to get a response, which may use the SQL tool.
    """
    response = agent_executor.invoke({"input": user_input})
    return response.get("output")