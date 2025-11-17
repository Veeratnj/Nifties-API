from fastapi import APIRouter
from app.schemas.schema import ChatRequest, ChatResponse
from app.services.chat_services import get_agent_response

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_with_agent(payload: ChatRequest):
    response = await get_agent_response(payload.message)
    return ChatResponse(response=response)
