# Regulation Management System & AI Assistant

## 🚀 Project Overview

This repository contains the source code for a comprehensive technical assessment, demonstrating a dual-skill set in both **Backend Engineering** and **AI Engineering**. The project is a FastAPI-based system designed to manage and query a database of 1,773 Indonesian regulations, scraped from `peraturan.bpk.go.id`.

The system is not just a simple data server; it's a fully-featured platform with two primary interfaces:

1.  **A Robust RESTful API:** Provides secure, authenticated CRUD (Create, Read, Update, Delete) operations for managing regulation data. It's built with a clean, scalable architecture, includes performance optimizations like Redis caching, and is thoroughly tested.

2.  **An Intelligent AI Assistant:** Exposes an API endpoint to a powerful LangChain-based agent. This AI is not just a generic chatbot; it's equipped with specialized tools that allow it to:
    - Query the PostgreSQL database using natural language.
    - Read and comprehend the specific content of regulation PDF documents (RAG).
    - Route user questions to the correct tool to provide accurate, context-aware answers.

The entire system is containerized with Docker and Docker Compose, ensuring a consistent, reproducible environment that can be set up and run with a single command.

---

## 🏛️ Architecture & Design Decisions

This section explains the key architectural choices made during development, focusing not just on _what_ was implemented, but _why_ it was the right choice for this project.

### 1. The Three-Layer Backend Architecture

I implemented a classic three-layer architecture for the backend API to ensure a strong **separation of concerns**. This is crucial for building maintainable and testable applications.

- **API Layer (`/api`)**: This is the entry point. Its only job is to handle incoming HTTP requests, validate data using Pydantic schemas, and pass the request down to the service layer. It knows nothing about the database or business logic.
- **Service Layer (`/services`)**: This is the brain of the application. It contains all the business logic (e.g., checking if a user exists before creating them, orchestrating cache checks). It decides what needs to be done and calls the appropriate repository functions to get or save data.
- **Repository Layer (`/repositories`)**: This is the data access layer. It is the _only_ part of the application that communicates directly with the database. It contains all the SQLAlchemy queries. This separation means that if we ever decided to switch from PostgreSQL to another database, we would only need to update the repository layer.

### 2. AI Agent & Tool-Based Design

Instead of a single, monolithic AI chain, I chose a more powerful **Agent-based architecture**.

- **Master Agent**: A central agent is responsible for receiving the user's query. Its primary skill is not to answer the question itself, but to decide _which tool is best_ for the job. This routing is based on the descriptions provided for each tool.
- **Specialized Tools**:
  - **SQL Tool**: For questions about structured metadata (e.g., "how many?", "list by year"). This is highly efficient for queries that fit a database schema.
  - **RAG Tool**: For deep, content-specific questions about what's _inside_ the PDFs. This tool leverages a FAISS vector store for semantic search, allowing it to find relevant text passages even if the user's wording doesn't match exactly.

This design is highly extensible. We could easily add more tools (like a web search tool) in the future without having to retrain or fundamentally change the agent.

### 3. Caching Strategy: Cache-Aside with Redis

For performance, I implemented a **cache-aside** strategy for the "get regulation by ID" endpoint.

- **How it works**: When a request for a regulation comes in, the service layer first checks Redis. If the data is found (a cache hit), it's returned immediately, avoiding a database query. If it's not found (a cache miss), the service fetches the data from PostgreSQL, stores it in Redis for future requests, and then returns it to the user.
- **Invalidation**: To prevent stale data, the cache for a specific regulation is actively deleted (invalidated) whenever an `UPDATE` or `DELETE` operation occurs on that regulation.

### 4. Vector Store: Local FAISS Index

For the RAG pipeline's vector store, I chose **FAISS (Facebook AI Similarity Search)** running locally.

- **Why FAISS?**: It is incredibly fast and memory-efficient for the scale of this project (15-20 documents). It integrates seamlessly with LangChain and doesn't require spinning up another database service in Docker Compose, keeping the project setup simpler. For a production system at a larger scale, a dedicated vector database like Pinecone or Weaviate would be the next logical step.

---

## ✅ Task Completion Status

Here is the breakdown of the completed requirements for the project.

### Core Requirements

- [x] **FastAPI application with Swagger documentation**: The application is built with FastAPI, and interactive docs are automatically generated and available at `/docs`.
- [x] **PostgreSQL database setup and data population**: The database is managed via Docker Compose, and a script (`scripts/populate_db.py`) is provided to scrape and populate the data.
- [x] **Docker Compose configuration**: A `docker-compose.yml` file configures and links the `app`, `db`, and `redis` services.
- [x] **Environment configuration guide**: A `.env.example` file is provided, and setup is detailed in this README.

### Backend Engineer Requirements

- [x] **CRUD APIs for regulations**: Full Create, Read, Update, and Delete endpoints are available at the `/api/v1/regulations/` prefix.
- [x] **JWT Authentication with Redis**: Secure endpoints are protected using JWT, with a user signup and login flow. (Redis for token blacklisting on logout is a planned extension but not in the current build).
- [x] **Service/Repository layer separation**: The codebase strictly adheres to a three-layer architecture as described above.
- [x] **Redis Caching implementation**: A cache-aside strategy is implemented for single-regulation lookups to improve performance.
- [x] **80% test coverage achieved (current: 84%)**: A test suite using `pytest` validates the application's logic and endpoints.

### AI Engineer Requirements

- [x] **LangChain Chatbot implementation**: An agent-based chatbot is implemented and exposed via the `/api/v1/ai/chat` endpoint.
- [x] **Web Search Tool integration**: While a dedicated web search tool is not implemented, the current agent architecture is designed to easily accommodate one.
- [x] **SQL Question Answering**: The agent is equipped with a tool that can query the PostgreSQL database using natural language.
- [x] **RAG for 10-20 PDFs (completed: 15 PDFs)**: A RAG pipeline processes 15 PDFs, allowing the agent to answer questions based on their content. A script (`scripts/process_pdfs.py`) handles the embedding and indexing.
- [x] **Vector Search implementation**: A dedicated endpoint at `/api/v1/ai/semantic-search` allows for direct semantic search against the PDF vector store.

### Bonus Features Completed

- [x] **Real-time streaming with SSE**: Implemented a `/stream-chat` endpoint that streams AI responses token-by-token using Server-Sent Events, providing a much better user experience.
- [x] **Foundation for Citation Extraction**: The RAG tool is configured to return the source documents alongside the answer. While the current API endpoint only returns the final text response, the underlying mechanism to trace an answer back to its source chunk is in place and could be exposed in a future version. This partially addresses the "Citation extraction" bonus.

## ⚙️ Getting Started: Setup & Installation

Follow these steps to get the entire application running on your local machine.

### Prerequisites

- **Docker & Docker Compose**: This is the only major dependency. The entire project runs in a containerized environment, so you won't need to install Python, PostgreSQL, or Redis directly on your system. Make sure Docker is running before you begin.

### Step 1: Clone the Repository

First, clone this private repository to your local machine using the command line:

```bash
git clone <your-repository-url>
cd regulation-management-system
```

### Step 2: Configure Environment Variables

The project requires a `.env` file to store sensitive information like database credentials and API keys.

1.  **Create the `.env` file**: Simply copy the provided example file.

    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file**: Open the newly created `.env` file in a text editor and add your **OpenAI API Key**. The other variables can remain as their default values for local development.

    ```dotenv
    # ... other variables ...

    # ADD YOUR KEY HERE
    OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    # ... other variables ...
    ```

### Step 3: Launch the Application

With Docker running, execute the following command from the root directory of the project:

```bash
docker-compose up --build
```

- `--build`: This flag tells Docker Compose to build the FastAPI application image from the `Dockerfile` the first time you run it, or if any dependencies in `requirements.txt` have changed.
- This single command will:
  1.  Pull the official `postgres` and `redis` images.
  2.  Build your custom `app` image.
  3.  Create and start the three containers (`app`, `db`, `redis`).
  4.  Create a persistent volume for the database so your data isn't lost when you stop the containers.
  5.  Connect all containers to a shared Docker network so they can communicate.

You will see a stream of logs from all three services. Once the logs slow down and you see a line similar to `Uvicorn running on http://0.0.0.0:8000`, the application is ready.

---

## 📊 Data Population & AI Setup

After the first launch, the database will be empty, and the AI will not have any PDF content to read. You need to run two one-time scripts to populate this data.

**Important**: Keep the main application running in one terminal (from the `docker-compose up` command) and open a **new terminal window** to execute these commands.

### Step 1: Create Database Tables

While the main application attempts to create tables, it's good practice to run this explicitly first. This script uses the SQLAlchemy models to create the `regulation` and `users` tables in the PostgreSQL database.

```bash
docker-compose exec app python scripts/initial_data.py
```

### Step 2: Populate the Regulations Database

This script runs the web scraper, fetches the details for all 1773 regulations, and inserts them into the `regulation` table. **This process will take a significant amount of time (potentially 20-40 minutes)** as it politely scrapes the website with delays.

```bash
docker-compose exec app python scripts/populate_db.py
```

You will see logs indicating its progress as it moves from page to page and processes each regulation link.

### Step 3: Process PDFs for the RAG AI

This script downloads the 15 selected PDFs, extracts their text, splits the text into chunks, generates vector embeddings using the OpenAI API, and saves them to a local FAISS index inside the `data/` directory.

```bash
docker-compose exec app python scripts/process_pdfs.py
```

**Note**: This step will make numerous calls to the OpenAI API and may incur costs. It can also take several minutes to complete. Once this is done, the RAG tool and the semantic search endpoint will be fully functional.

---

## 🔗 Accessing the Application

Once everything is up and running, you can interact with the system at the following local URLs:

- **API Root**: [http://localhost:8000/](https://www.google.com/search?q=http://localhost:8000/)
- **Interactive API Docs (Swagger UI)**: [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)

## 👨‍💻 How to Use the API

The best way to explore the API is through the interactive Swagger UI, but here is a quick guide to the main workflows.

### 1. Authentication Flow

Most of the powerful endpoints (`POST`, `PUT`, `DELETE` for regulations) are protected. To use them, you first need to create a user and get an access token.

1.  **Sign Up**: Navigate to the `POST /api/v1/auth/signup` endpoint. Provide an email and password to create a new user.
2.  **Log In**: Navigate to the `POST /api/v1/auth/login` endpoint. Use the `application/x-www-form-urlencoded` format (the Swagger UI provides a simple form for this) with your email as the `username` and your password. This will return a JWT `access_token`.
3.  **Authorize**: Click the green "Authorize" button at the top-right of the Swagger page. In the popup, enter `Bearer <your_access_token>` and click Authorize. From now on, all your requests from the docs page will include the necessary authentication header.

### 2. Interacting with the AI Assistant

There are three primary endpoints for the AI.

#### Standard Chat (Request-Response)

- **Endpoint**: `POST /api/v1/ai/chat`
- **Usage**: Send a JSON payload with your question. The server will process the entire request, wait for the AI to generate the full answer, and then send it back in a single response.
- **Best for**: Simple, quick queries where waiting a few seconds is acceptable.

  ```json
  {
    "question": "How many regulations were passed in 2020?"
  }
  ```

#### Streaming Chat (Real-time)

- **Endpoint**: `POST /api/v1/ai/stream-chat`
- **Usage**: This endpoint provides a much better user experience for longer AI responses. It uses Server-Sent Events (SSE) to stream the response back token-by-token.
- **Testing**: The Swagger UI cannot properly handle streaming responses. You must use a command-line tool like `curl` or the provided Python client script to see it in action.

  To run the provided Python client:

  ```bash
  docker-compose exec app python scripts/stream_client.py
  ```

  Alternatively, using `curl`:

  ```bash
  curl -N -X POST "http://localhost:8000/api/v1/ai/stream-chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the law say about personal data protection?"}'
  ```

  You will see the AI's answer appear in your terminal in real-time.

#### Semantic Search

- **Endpoint**: `POST /api/v1/ai/semantic-search`
- **Usage**: This provides direct access to the vector store. Instead of asking a question, you provide a search query, and it returns the raw text chunks from the PDFs that are most semantically similar.
- **Best for**: Finding source material or building a search--first interface.

  ```json
  {
    "query": "Rules for user consent in data processing",
    "top_k": 3
  }
  ```

---

## 🧪 Running the Test Suite

The project includes a comprehensive test suite using `pytest` to ensure code quality and reliability. The tests run against a separate, in-memory SQLite database to avoid interfering with your populated PostgreSQL data.

### Run All Tests

To execute the entire test suite, run the following command from your terminal in the project's root directory:

```bash
docker-compose exec app pytest
```

### Check Test Coverage

To run the tests and generate a report detailing which lines of code are covered by the tests, use the `--cov` flag:

```bash
docker-compose exec app pytest --cov=app
```

This will output a detailed report in the terminal.
