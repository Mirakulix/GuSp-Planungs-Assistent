"""
Azure OpenAI Service integration for Pfadi AI Assistant.
"""

import json
import logging
from typing import List, Optional, Dict, Any
from openai import AsyncAzureOpenAI
from openai.types.chat import ChatCompletion
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class AzureOpenAIService:
    """Service for interacting with Azure OpenAI."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client."""
        self.client: Optional[AsyncAzureOpenAI] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Azure OpenAI client if credentials are available."""
        if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_API_KEY:
            logger.warning(
                "Azure OpenAI credentials not configured. Chat functionality will be limited.",
                endpoint_configured=bool(settings.AZURE_OPENAI_ENDPOINT),
                key_configured=bool(settings.AZURE_OPENAI_API_KEY)
            )
            return
        
        try:
            self.client = AsyncAzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version="2024-02-15-preview"
            )
            logger.info("Azure OpenAI client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Azure OpenAI client", error=str(e))
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        functions: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using Azure OpenAI.
        
        Args:
            messages: List of message objects with 'role' and 'content'
            model: Model deployment name (defaults to configured deployment)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            functions: Function definitions for function calling
            
        Returns:
            Dict containing the response and metadata
        """
        if not self.client:
            logger.warning("Azure OpenAI client not available, returning mock response")
            return self._get_mock_response(messages[-1].get("content", ""))
        
        try:
            deployment_name = model or settings.AZURE_OPENAI_DEPLOYMENT_NAME
            
            # Prepare request parameters
            request_params = {
                "model": deployment_name,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            
            if functions:
                request_params["functions"] = functions
                request_params["function_call"] = "auto"
            
            logger.info(
                "Sending chat completion request",
                model=deployment_name,
                message_count=len(messages),
                temperature=temperature
            )
            
            response: ChatCompletion = await self.client.chat.completions.create(**request_params)
            
            # Extract response data
            choice = response.choices[0]
            message = choice.message
            
            result = {
                "message": message.content,
                "role": message.role,
                "function_call": None,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "model": deployment_name,
                "finish_reason": choice.finish_reason
            }
            
            # Handle function calls
            if message.function_call:
                result["function_call"] = {
                    "name": message.function_call.name,
                    "arguments": message.function_call.arguments
                }
            
            logger.info(
                "Chat completion successful",
                tokens_used=result["usage"]["total_tokens"],
                finish_reason=result["finish_reason"]
            )
            
            return result
            
        except Exception as e:
            logger.error("Chat completion failed", error=str(e))
            return {
                "message": "Entschuldigung, es gab einen Fehler bei der Verarbeitung deiner Anfrage. Bitte versuche es später erneut.",
                "role": "assistant",
                "error": str(e)
            }
    
    async def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """
        Generate embeddings for text using Azure OpenAI.
        
        Args:
            text: Text to generate embeddings for
            model: Embedding model deployment name
            
        Returns:
            List of embedding values
        """
        if not self.client:
            logger.warning("Azure OpenAI client not available for embeddings")
            return [0.0] * 1536  # Return dummy embedding
        
        try:
            deployment_name = model or settings.AZURE_EMBEDDING_DEPLOYMENT_NAME
            
            response = await self.client.embeddings.create(
                model=deployment_name,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            logger.info(
                "Embedding generation successful",
                text_length=len(text),
                embedding_dimensions=len(embedding)
            )
            
            return embedding
            
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            return [0.0] * 1536  # Return dummy embedding
    
    def _get_mock_response(self, user_message: str) -> Dict[str, Any]:
        """Generate a mock response when Azure OpenAI is not available."""
        
        # Simple keyword-based responses for demonstration
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["spiel", "game", "aktivität"]):
            response = "Ich kann dir beim Finden von Spielen helfen! Da ich momentan nicht mit Azure OpenAI verbunden bin, kann ich dir empfehlen, die Spielesuche zu verwenden, um passende Aktivitäten zu finden."
        elif any(word in message_lower for word in ["plan", "heimstunde", "meeting"]):
            response = "Gerne helfe ich dir bei der Planung einer Heimstunde! Nutze die Planungsfunktion, um strukturierte Vorschläge zu erhalten."
        elif any(word in message_lower for word in ["pfadfinder", "scout", "gesetz"]):
            response = "Als Pfadfinder-Assistent kann ich dir Informationen zur Pfadfinderbewegung geben. Für detaillierte Antworten benötige ich eine Verbindung zu Azure OpenAI."
        else:
            response = f"Du hast gesagt: '{user_message}'. Ich bin hier, um dir bei der Pfadfinderarbeit zu helfen! Konfiguriere Azure OpenAI für erweiterte KI-Funktionen."
        
        return {
            "message": response,
            "role": "assistant",
            "mock": True,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }
    
    def is_available(self) -> bool:
        """Check if Azure OpenAI service is available."""
        return self.client is not None


# Global service instance
azure_openai_service = AzureOpenAIService()