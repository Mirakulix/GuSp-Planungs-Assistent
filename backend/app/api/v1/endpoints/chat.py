"""
Chatbot endpoints for conversational AI interactions.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import uuid
from datetime import datetime

from app.core.config import settings

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None
    function_call_data: Optional[dict] = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_context: Optional[dict] = None


class SuggestedAction(BaseModel):
    text: str
    action: str
    data: Optional[dict] = None


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    data: Optional[dict] = None
    suggested_actions: List[SuggestedAction] = []
    timestamp: datetime


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for conversational AI."""
    
    if not settings.ENABLE_CHATBOT:
        raise HTTPException(status_code=501, detail="Chatbot feature is disabled")
    
    # Generate conversation ID if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # TODO: Implement actual chatbot logic with Azure OpenAI
    # For now, return a simple mock response
    
    response_message = f"Hallo! Du hast gefragt: '{request.message}'. "
    
    # Simple keyword-based responses for demo
    message_lower = request.message.lower()
    
    if any(word in message_lower for word in ["spiel", "game", "aktivität"]):
        response_message += "Ich kann dir beim Finden von Spielen helfen! Sage mir, wie viele Teilnehmer ihr seid und wie lange das Spiel dauern soll."
        suggested_actions = [
            SuggestedAction(
                text="🎯 Spiele suchen",
                action="search_games",
                data={}
            ),
            SuggestedAction(
                text="📋 Heimstunde planen",
                action="plan_heimstunde",
                data={}
            )
        ]
    elif any(word in message_lower for word in ["plan", "heimstunde", "meeting"]):
        response_message += "Gerne helfe ich dir bei der Planung einer Heimstunde! Erzähle mir mehr über deine Gruppe und was ihr machen möchtet."
        suggested_actions = [
            SuggestedAction(
                text="📅 Neue Heimstunde planen",
                action="create_plan",
                data={}
            ),
            SuggestedAction(
                text="🔍 Themenvorschläge",
                action="suggest_themes",
                data={}
            )
        ]
    elif any(word in message_lower for word in ["pfadfinder", "scout", "gesetz", "law"]):
        response_message += "Ich kann dir Fragen zur Pfadfinderbewegung beantworten! Was möchtest du wissen?"
        suggested_actions = [
            SuggestedAction(
                text="📚 Pfadfindergesetze",
                action="get_scout_laws",
                data={}
            ),
            SuggestedAction(
                text="🌍 Weltweite Verbundenheit",
                action="explain_scouting",
                data={}
            )
        ]
    else:
        response_message += "Ich bin hier, um dir bei der Planung von Pfadfinderaktivitäten zu helfen. Frag mich nach Spielen, Heimstunden oder Pfadfinderwissen!"
        suggested_actions = [
            SuggestedAction(
                text="🎯 Spiele suchen",
                action="search_games",
                data={}
            ),
            SuggestedAction(
                text="📅 Heimstunde planen",
                action="plan_heimstunde",
                data={}
            ),
            SuggestedAction(
                text="❓ Pfadfinderfragen",
                action="ask_scouting",
                data={}
            )
        ]
    
    return ChatResponse(
        message=response_message,
        conversation_id=conversation_id,
        suggested_actions=suggested_actions,
        timestamp=datetime.utcnow()
    )


@router.get("/{conversation_id}/history", response_model=List[ChatMessage])
async def get_conversation_history(conversation_id: str):
    """Get conversation history for a specific conversation."""
    
    # TODO: Implement actual conversation history retrieval
    # For now, return empty list
    return []


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation and its history."""
    
    # TODO: Implement actual conversation deletion
    return {"message": "Conversation deleted", "conversation_id": conversation_id}