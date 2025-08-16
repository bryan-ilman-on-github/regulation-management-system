from fastapi import APIRouter
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
    search_results = vector_search_service.semantic_search(query=request.query, k=request.top_k)
    return {"results": search_results}