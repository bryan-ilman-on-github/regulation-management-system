import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ...ai import chat_service, vector_search_service
from ...schemas.chat import ChatRequest
from ...schemas.search import SearchRequest, SearchResponse

router = APIRouter()


@router.post("/chat")
def handle_chat(request: ChatRequest):
    """
    Endpoint to handle an intelligent chat conversation using an agent.
    """
    # Call the new agent-based service function
    response_content = chat_service.get_intelligent_response(request.question)
    return {"response": response_content}


@router.post("/semantic-search", response_model=SearchResponse)
def handle_semantic_search(request: SearchRequest):
    """
    Performs a direct semantic search on the document vector store.
    """
    search_results = vector_search_service.semantic_search(
        query=request.query, k=request.top_k
    )
    return {"results": search_results}


# This is the new async generator that will be used by the endpoint
async def format_stream_for_sse(user_question: str):
    """
    Calls the streaming service and formats each token for Server-Sent Events (SSE).
    """
    async for token in chat_service.get_intelligent_response_stream(user_question):
        yield f"data: {json.dumps({'token': token})}\n\n"


@router.post("/stream-chat")
async def handle_stream_chat(request: ChatRequest):
    """

    Handles a streaming chat conversation using Server-Sent Events (SSE).
    """
    # The endpoint now directly calls the new formatting generator
    return StreamingResponse(
        format_stream_for_sse(request.question), media_type="text/event-stream"
    )
