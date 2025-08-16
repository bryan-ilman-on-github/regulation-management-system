from fastapi import APIRouter
from ...ai import chat_service
from ...schemas.chat import ChatRequest

router = APIRouter()

@router.post("/chat")
def handle_chat(request: ChatRequest):
    """
    Endpoint to handle an intelligent chat conversation using an agent.
    """
    # Call the new agent-based service function
    response_content = chat_service.get_intelligent_response(request.question)
    return {"response": response_content}