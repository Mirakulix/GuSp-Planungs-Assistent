"""
Chatbot endpoints for conversational AI interactions.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import structlog

from app.core.config import settings
from app.services.chat_service import pfadi_chat_service

logger = structlog.get_logger()
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
    usage: Optional[dict] = None
    mock_response: Optional[bool] = None


class ChatStatus(BaseModel):
    azure_openai_available: bool
    features_enabled: dict
    deployment_info: dict


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for conversational AI powered by Azure OpenAI."""
    
    if not settings.ENABLE_CHATBOT:
        raise HTTPException(status_code=501, detail="Chatbot feature is disabled")
    
    logger.info(
        "Processing chat request",
        message_length=len(request.message),
        has_conversation_id=bool(request.conversation_id),
        has_user_context=bool(request.user_context)
    )
    
    try:
        # Process the message using our chat service
        response = await pfadi_chat_service.process_message(
            user_message=request.message,
            conversation_id=request.conversation_id,
            user_context=request.user_context
        )
        
        # Convert suggested actions to the correct format
        suggested_actions = [
            SuggestedAction(**action) for action in response["suggested_actions"]
        ]
        
        logger.info(
            "Chat request processed successfully",
            conversation_id=response["conversation_id"],
            response_length=len(response["message"]),
            actions_count=len(suggested_actions),
            mock_response=response.get("mock_response", False)
        )
        
        return ChatResponse(
            message=response["message"],
            conversation_id=response["conversation_id"],
            data=response.get("data"),
            suggested_actions=suggested_actions,
            timestamp=response["timestamp"],
            usage=response.get("usage"),
            mock_response=response.get("mock_response")
        )
        
    except Exception as e:
        logger.error("Error processing chat request", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Fehler bei der Verarbeitung der Nachricht. Bitte versuche es erneut."
        )


@router.get("/status", response_model=ChatStatus)
async def get_chat_status():
    """Get the current status of the chat service and Azure integrations."""
    
    from app.services.azure_openai import azure_openai_service
    
    return ChatStatus(
        azure_openai_available=azure_openai_service.is_available(),
        features_enabled={
            "chatbot": settings.ENABLE_CHATBOT,
            "game_search": settings.ENABLE_GAME_SEARCH,
            "planning": settings.ENABLE_PLANNING,
            "camp_planning": settings.ENABLE_CAMP_PLANNING,
            "communication": settings.ENABLE_COMMUNICATION
        },
        deployment_info={
            "chat_model": settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            "embedding_model": settings.AZURE_EMBEDDING_DEPLOYMENT_NAME,
            "endpoint_configured": bool(settings.AZURE_OPENAI_ENDPOINT),
            "api_key_configured": bool(settings.AZURE_OPENAI_API_KEY)
        }
    )


@router.get("/{conversation_id}/history", response_model=List[ChatMessage])
async def get_conversation_history(conversation_id: str):
    """Get conversation history for a specific conversation."""
    
    try:
        history = pfadi_chat_service.get_conversation_history(conversation_id)
        
        # Convert to response format
        chat_messages = []
        for message in history:
            chat_messages.append(ChatMessage(
                role=message["role"],
                content=message["content"],
                timestamp=datetime.utcnow()  # TODO: Store actual timestamps
            ))
        
        logger.info(
            "Retrieved conversation history",
            conversation_id=conversation_id,
            message_count=len(chat_messages)
        )
        
        return chat_messages
        
    except Exception as e:
        logger.error("Error retrieving conversation history", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Abrufen der Unterhaltungshistorie"
        )


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation and its history."""
    
    try:
        success = pfadi_chat_service.clear_conversation(conversation_id)
        
        if success:
            logger.info("Conversation deleted", conversation_id=conversation_id)
            return {
                "message": "Unterhaltung erfolgreich gelöscht",
                "conversation_id": conversation_id
            }
        else:
            logger.warning("Conversation not found for deletion", conversation_id=conversation_id)
            raise HTTPException(
                status_code=404,
                detail="Unterhaltung nicht gefunden"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting conversation", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Löschen der Unterhaltung"
        )


@router.post("/{conversation_id}/export")
async def export_conversation(conversation_id: str):
    """Export conversation history for download."""
    
    try:
        history = pfadi_chat_service.get_conversation_history(conversation_id)
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail="Unterhaltung nicht gefunden oder leer"
            )
        
        # Format for export
        export_data = {
            "conversation_id": conversation_id,
            "exported_at": datetime.utcnow().isoformat(),
            "message_count": len(history),
            "messages": history
        }
        
        logger.info(
            "Conversation exported",
            conversation_id=conversation_id,
            message_count=len(history)
        )
        
        return export_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error exporting conversation", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Exportieren der Unterhaltung"
        )