# Maintainer's Guide & Code Documentation

Welcome, developer! This document is a deep dive into the internal workings of the Regulation Management System. Its purpose is to get you up to speed on the architecture, code structure, and key components so you can confidently maintain and extend the application.

## ToC

- [1. Core Application Structure & Entrypoint](#1-core-application-structure--entrypoint)
  - [`app/main.py` - The Entrypoint](#appmainpy---the-entrypoint)
- [2. Foundational Services (`app/core`)](#2-foundational-services-appcore)
  - [`database.py`](#databasepy)
  - [`security.py`](#securitypy)
  - [`redis_client.py`](#redis_clientpy)
- [3. Backend Architecture: A Request's Journey](#3-backend-architecture-a-requests-journey)
  - [Step 1: API Layer (`app/api/endpoints/regulations.py`)](#step-1-api-layer-appapiendpointsregulationspy)
  - [Step 2: Service Layer (`app/services/regulation_service.py`)](#step-2-service-layer-appservicesregulation_servicepy)
  - [Step 3: Repository Layer (`app/repositories/regulation_repository.py`)](#step-3-repository-layer-apprepositoriesregulation_repositorypy)
- [4. Models vs. Schemas: The Data Contracts](#4-models-vs-schemas-the-data-contracts)
  - [Models (`app/models/`)](#models-appmodels)
  - [Schemas (`app/schemas/`)](#schemas-appschemas)
- [5. AI Architecture: An Agent with Tools](#5-ai-architecture-an-agent-with-tools)
  - [`app/ai/tools/sql_tool.py`](#appaitoolssql_toolpy)
  - [`app/ai/tools/rag_tool.py`](#appaitoolsrag_toolpy)
  - [`app/ai/chat_service.py` - The Master Agent](#appaichat_servicepy---the-master-agent)
  - [`app/api/endpoints/chat.py` - The AI Endpoints](#appapiendpointschatpy---the-ai-endpoints)

## 1. Core Application Structure & Entrypoint

The heart of the application lives in the `/app` directory. The project follows a standard, modular structure that separates concerns, making the codebase clean and easy to navigate.

### `app/main.py` - The Entrypoint

This file is the starting point of the FastAPI application. Its responsibilities are minimal but crucial:

- **FastAPI App Instantiation**: It creates the main `app = FastAPI(...)` instance, which is the root of the application. This is where global configuration like the API title and description is set.
- **Router Inclusion**: The application's endpoints are not defined directly in `main.py`. Instead, they are organized into separate "router" objects in the `app/api/endpoints/` directory. `main.py` is responsible for importing these routers and including them in the main app with a specific URL prefix and tag. This keeps the API routes modular and organized by feature.
- **Root Endpoint**: It defines a simple `GET /` endpoint, which is useful for health checks to confirm that the API is running.

```python
# app/main.py

# ... imports ...

# Create the main FastAPI application instance
app = FastAPI(
    title="Regulation Management System API",
    # ...
)

# Include the router for authentication endpoints under the "/api/v1/auth" prefix
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

# Include the router for regulation CRUD endpoints
app.include_router(
    regulations.router, prefix="/api/v1/regulations", tags=["Regulations"]
)

# Include the router for AI chat endpoints
app.include_router(chat.router, prefix="/api/v1/ai", tags=["AI"])

# ...
```

## 2\. Foundational Services (`app/core`)

The `app/core/` directory contains the foundational, cross-cutting concerns of the application. These modules provide services that are used throughout the backend.

### `database.py`

- **Purpose**: Manages all aspects of the PostgreSQL database connection.
- **Key Components**:
  - `engine`: The core SQLAlchemy engine that connects to the database using the `DATABASE_URL` from the environment configuration.
  - `SessionLocal`: A "session factory" used to create new database sessions. Each API request gets its own session, ensuring that work is transactional and isolated.
  - `Base`: The declarative base class for all SQLAlchemy models. Any class that inherits from `Base` will be mapped to a database table.
  - `get_db()`: This is a **FastAPI dependency**. It's a generator function that yields a new database session for a single request and ensures the session is always closed afterward, even if errors occur. This is the standard, correct way to handle database sessions in FastAPI.

### `security.py`

- **Purpose**: Handles all authentication and security-related logic.
- **Key Functions**:
  - `pwd_context`: An instance of `CryptContext` from the `passlib` library, configured to use `bcrypt` for password hashing.
  - `verify_password()`: Compares a plain-text password with a hashed password to see if they match.
  - `get_password_hash()`: Takes a plain-text password and returns its secure hash.
  - `create_access_token()`: Creates the JWT (JSON Web Token). It takes a user's identity (e.g., their email), adds an expiration time, and signs it with the `SECRET_KEY` from the environment configuration.

### `redis_client.py`

- **Purpose**: Manages the connection to the Redis server for caching.
- **Key Components**:
  - **Lazy Initialization**: The Redis client is initialized "lazily." The connection is not established when the application starts but only on the first call to `get_redis_client()`. This prevents connection issues during application startup, especially in test environments.
  - `set_cache`, `get_cache`, `delete_cache`: These are helper functions that abstract the Redis logic. They automatically handle the serialization (Python dict to JSON string) and deserialization (JSON string back to Python dict) of cached data.

## 3\. Backend Architecture: A Request's Journey

The application follows a strict **Three-Layer Architecture**. Let's trace a `GET /api/v1/regulations/{regulation_id}` request to understand the flow.

### Step 1: API Layer (`app/api/endpoints/regulations.py`)

- **Role**: The "front door." It handles the HTTP request and response.
- **Process**:
  1.  A request hits the `@router.get("/{regulation_id}", ...)` decorator.
  2.  FastAPI validates that `regulation_id` is a valid UUID.
  3.  It calls the `get_db` dependency to get an active database session.
  4.  It calls the corresponding service function (`service.get_regulation`) and passes the `db` session and `regulation_id` to it.
  5.  It takes the return value from the service, formats it as JSON based on the `response_model`, and sends it back to the client.

### Step 2: Service Layer (`app/services/regulation_service.py`)

- **Role**: The "brain." It contains the business logic.
- **Process**:
  1.  The `get_regulation` function receives the call from the API layer.
  2.  **It checks the cache first**. It constructs a `cache_key` and calls `get_cache()`. If the data exists, it's returned immediately, and the process stops here.
  3.  If it's a cache miss, it calls the repository function (`repo.get`) to fetch the data from the database.
  4.  It performs logic, such as checking if the regulation was actually found. If not, it raises an `HTTPException`, which FastAPI automatically converts into a `404 Not Found` response.
  5.  If the data is found, it uses the Pydantic `Regulation` model to serialize the SQLAlchemy object into a dictionary.
  6.  It calls `set_cache` to store the result in Redis for the next request.
  7.  It returns the data to the API layer.

### Step 3: Repository Layer (`app/repositories/regulation_repository.py`)

- **Role**: The "hands." The only layer that touches the database.
- **Process**:
  1.  The `get` function receives the call from the service layer.
  2.  It executes a single, clear SQLAlchemy query: `db.query(Regulation).filter(...).first()`.
  3.  It returns the raw SQLAlchemy model object (or `None`) back to the service layer. It contains no other logic.

## 4\. Models vs. Schemas: The Data Contracts

A key concept in this application is the separation of database models from API schemas.

### Models (`app/models/`)

- **Purpose**: Define the structure of your **database tables**.
- **Technology**: SQLAlchemy `declarative_base`.
- **Example (`user.py`)**: The `User` class defines the `users` table with its columns (`id`, `email`, `hashed_password`). It's a direct representation of your database schema in Python.

### Schemas (`app/schemas/`)

- **Purpose**: Define the shape of the data for your **API requests and responses**.
- **Technology**: Pydantic `BaseModel`.
- **Example (`user.py`)**:
  - `UserCreate`: Defines what the API expects when a new user signs up (an `email` and a `password`). It ensures you don't accidentally expose the `hashed_password` field in requests.
  - `User`: Defines what the API will return about a user (their `id`, `email`, and `is_active` status). Notice it _does not_ include the password, preventing it from ever being leaked in an API response.

This separation is vital for security and for creating a stable API contract that is independent of your internal database structure.

## 5. AI Architecture: An Agent with Tools

The AI system is not a single, monolithic prompt. It's built as an **Agent**, a more advanced concept in LangChain. An agent acts like a smart router that has access to a set of specialized **Tools**. When it receives a question, its first job is to decide _which tool to use_.

This **Agent-based design** is powerful because:

1.  **It's Extensible**: We can easily add new tools (e.g., a tool to search the live web, a tool to perform calculations) without rewriting the entire AI. We just give the new tool to the agent.
2.  **It's More Accurate**: Each tool is highly specialized for a single task. The SQL tool is great at database queries, and the RAG tool is great at searching text. The agent ensures the query goes to the right specialist.
3.  **It's More Observable**: Because the agent's `verbose` flag is set to `True`, you can see its "chain of thought" in the Docker logs. It will explicitly state which tool it's choosing and what input it's passing to it, which is invaluable for debugging.

### `app/ai/tools/sql_tool.py`

- **Purpose**: This tool gives the AI the ability to query the PostgreSQL database using natural language.
- **How it Works**:
  1.  It uses LangChain's `create_sql_agent`, which is a pre-built, highly optimized agent specifically for this task.
  2.  It connects to our database using the same SQLAlchemy `engine` as the rest of the application. LangChain uses this connection to inspect the table schemas (so it knows about the `regulation` table and its columns) and to execute the queries it generates.
  3.  When the agent decides to use this tool, it passes the user's question to the `query_database` function. The SQL agent then:
      - Analyzes the question.
      - Generates a SQL `SELECT` statement.
      - Executes the query against the database.
      - Analyzes the results.
      - Generates a final, human-readable answer.
- **Lazy Initialization**: The `get_sql_agent` function uses a lazy-loading pattern. The expensive objects (the LLM and the database connection) are only initialized the _first time_ the tool is ever used in the application's lifecycle, not on startup. This makes the application start faster.

### `app/ai/tools/rag_tool.py`

- **Purpose**: This is the "document reading" tool. It answers questions based on the specific text content of the regulation PDFs. RAG stands for **Retrieval-Augmented Generation**.
- **How it Works**:
  1.  **Retrieval**: When the `query_document_content` function is called, it first takes the user's question and performs a _semantic search_ on the FAISS vector store. The `as_retriever()` method finds the text chunks from the PDFs that are most relevant to the question.
  2.  **Augmentation**: It then "augments" the prompt by stuffing these retrieved text chunks into the context window along with the original question.
  3.  **Generation**: Finally, it sends this augmented prompt to the LLM. The LLM's task is now much easier: instead of needing to "know" the answer, it just needs to synthesize an answer based on the provided text.
- **Key Component**: The `RetrievalQA` chain from LangChain orchestrates this entire process seamlessly. We've configured it to also return the source documents, which is the foundation for the citation bonus feature.

### `app/ai/chat_service.py` - The Master Agent

- **Purpose**: This service is the central hub for the AI. It creates the master agent and exposes the logic to the API endpoints.
- **Key Components**:
  - `tools` list: This is where the agent is given its tools. The `Tool` objects are defined with a `name`, the `func` to call, and a `description`. **The `description` is the most important part**, as the agent uses these descriptions to decide which tool to use.
  - `prompt`: A `ChatPromptTemplate` is defined to give the agent its core identity ("You are a powerful assistant...") and to structure the conversation.
  - `agent_executor`: This is the final, runnable agent that combines the LLM, the prompt, and the tools.
- **Handling Streaming vs. Non-Streaming**:
  - `get_intelligent_response()`: This is the standard, non-streaming function. It calls `agent_executor.invoke()` which blocks until the full response is ready.
  - `get_intelligent_response_stream()`: This is the more complex, asynchronous generator for streaming. It uses an `AsyncIteratorCallbackHandler` from LangChain. This handler "listens" for tokens as they are generated by the LLM and puts them into an async queue. The function can then `yield` these tokens one by one as they become available, without waiting for the full response.

### `app/api/endpoints/chat.py` - The AI Endpoints

This file exposes the AI's capabilities to the outside world via three distinct endpoints.

1.  **`POST /chat`**: The standard, request-response endpoint. It calls the `get_intelligent_response` service function and is simple and reliable.
2.  **`POST /stream-chat`**: The streaming endpoint. It returns a `StreamingResponse` object from FastAPI. Its content is the `format_stream_for_sse` async generator, which calls the streaming service and formats each token into the Server-Sent Event `data: {...}\n\n` format that web clients can easily parse.
3.  **`POST /semantic-search`**: This endpoint bypasses the agent entirely and provides direct access to the RAG pipeline's retriever. It calls the `vector_search_service.semantic_search` function, which performs a similarity search on the FAISS index and returns the raw text chunks and their similarity scores. This is useful for building search-focused UIs or for debugging the retrieval process.
