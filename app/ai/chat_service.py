import asyncio
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.callbacks import AsyncIteratorCallbackHandler

from ..core.config import OPENAI_API_KEY
from .tools.rag_tool import query_document_content
from .tools.sql_tool import query_database

# --- This non-streaming agent is for regular chat endpoint ---
# Initialize the standard LLM for non-streaming responses
non_streaming_llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY, model_name="gpt-4-turbo-preview", temperature=0
)

# Define the tools the agent can use
tools = [
    Tool(
        name="RegulationDatabase",
        func=query_database,
        description="""Use this tool to answer questions about Indonesian regulations.
        This includes counting regulations, listing them by year, finding status,
        or any other question that can be answered by querying a SQL table
        named 'regulation'.""",
    ),
    Tool(
        name="RegulationDocumentSearch",
        func=query_document_content,
        description="""Use this tool for detailed questions about the SPECIFIC CONTENT,
        articles, clauses, or definitions inside a regulation document.
        The input should be a very specific question about the document's text.""",
    ),
]

# Create the prompt for the master agent
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a powerful assistant that can answer questions about Indonesian regulations.",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_openai_functions_agent(non_streaming_llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def get_intelligent_response(user_input: str) -> str:
    """Invokes the master agent to get a single, complete response."""
    response = agent_executor.invoke({"input": user_input})
    return response.get("output")


# --- This new async generator is for streaming endpoint ---
async def get_intelligent_response_stream(user_input: str):
    """
    Streams the agent's final response token-by-token using a callback handler.
    """
    # Create a callback handler to capture the streamed tokens
    callback = AsyncIteratorCallbackHandler()

    # Create a streaming-enabled LLM instance with the callback
    streaming_llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model_name="gpt-4-turbo-preview",
        temperature=0,
        streaming=True,  # Enable streaming
        callbacks=[callback],  # Pass the callback handler
    )

    # Create the agent and executor using the streaming LLM
    agent = create_openai_functions_agent(streaming_llm, tools, prompt)
    agent_executor_streaming = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Run the agent in a background task so we can stream tokens immediately
    task = asyncio.create_task(agent_executor_streaming.ainvoke({"input": user_input}))

    # Yield tokens as they become available from the callback handler
    try:
        async for token in callback.aiter():
            yield token
    except Exception as e:
        print(f"Caught exception in generator: {e}")
    finally:
        # Ensure the background task is complete
        await task
