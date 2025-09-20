"""
Chat service implementing Pfadi-specific conversation logic.
"""

import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog

from app.services.azure_openai import azure_openai_service
from app.core.config import settings

logger = structlog.get_logger()


class PfadiChatService:
    """Chat service specifically designed for Pfadi AI Assistant."""
    
    # Function definitions for OpenAI function calling
    AVAILABLE_FUNCTIONS = {
        "search_games": {
            "name": "search_games",
            "description": "Sucht nach Spielen und Aktivitäten basierend auf Kriterien wie Teilnehmeranzahl, Dauer oder Thema",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "Suchbegriff für Spiele (z.B. 'Teambuilding', 'Vertrauen', 'Outdoor')"
                    },
                    "duration_max": {
                        "type": "integer", 
                        "description": "Maximale Dauer in Minuten"
                    },
                    "participant_count": {
                        "type": "integer", 
                        "description": "Anzahl der Teilnehmer"
                    },
                    "location": {
                        "type": "string", 
                        "enum": ["indoor", "outdoor", "both"],
                        "description": "Wo das Spiel stattfinden soll"
                    },
                    "age_group": {
                        "type": "string",
                        "description": "Altersgruppe (z.B. '10-13')"
                    }
                },
                "required": ["query"]
            }
        },
        "create_heimstunde_plan": {
            "name": "create_heimstunde_plan",
            "description": "Erstellt einen strukturierten Plan für eine Heimstunde",
            "parameters": {
                "type": "object",
                "properties": {
                    "theme": {
                        "type": "string", 
                        "description": "Thema der Heimstunde (z.B. 'Freundschaft', 'Mut', 'Teamwork')"
                    },
                    "duration": {
                        "type": "integer", 
                        "description": "Gesamtdauer in Minuten"
                    },
                    "participant_count": {
                        "type": "integer",
                        "description": "Anzahl der Teilnehmer"
                    },
                    "location": {
                        "type": "string",
                        "enum": ["indoor", "outdoor", "flexible"],
                        "description": "Wo die Heimstunde stattfindet"
                    },
                    "pedagogical_goals": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Pädagogische Ziele (z.B. 'Teambuilding', 'Kreativität', 'Kommunikation')"
                    }
                },
                "required": ["duration", "participant_count"]
            }
        },
        "get_pfadfinder_knowledge": {
            "name": "get_pfadfinder_knowledge",
            "description": "Beantwortet Fragen zum Pfadfinderwissen, Gesetzen, Traditionen und pädagogischen Konzepten",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string", 
                        "description": "Die Frage zum Pfadfinderwissen"
                    },
                    "age_appropriate": {
                        "type": "boolean", 
                        "description": "Ob die Antwort für Kinder (10-13 Jahre) aufbereitet werden soll"
                    }
                },
                "required": ["question"]
            }
        }
    }
    
    def __init__(self):
        """Initialize the chat service."""
        self.conversation_memory: Dict[str, List[Dict]] = {}
    
    async def process_message(
        self,
        user_message: str,
        conversation_id: Optional[str] = None,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            user_message: The user's input message
            conversation_id: ID for conversation continuity
            user_context: Additional context about the user
            
        Returns:
            Dict containing response and metadata
        """
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Build conversation history
        messages = self._build_conversation_messages(
            user_message, 
            conversation_id, 
            user_context
        )
        
        # Get AI response
        try:
            if azure_openai_service.is_available():
                response = await self._get_ai_response(messages, conversation_id)
            else:
                response = self._get_fallback_response(user_message)
        except Exception as e:
            logger.error("Error processing message", error=str(e))
            response = {
                "message": "Entschuldigung, es gab einen technischen Fehler. Bitte versuche es erneut.",
                "error": True
            }
        
        # Update conversation memory
        self._update_conversation_memory(conversation_id, user_message, response)
        
        # Generate suggested actions
        suggested_actions = self._generate_suggested_actions(response, user_message)
        
        return {
            "message": response.get("message", "Keine Antwort erhalten."),
            "conversation_id": conversation_id,
            "data": response.get("function_data"),
            "suggested_actions": suggested_actions,
            "timestamp": datetime.utcnow(),
            "usage": response.get("usage", {}),
            "mock_response": response.get("mock", False)
        }
    
    def _build_conversation_messages(
        self,
        user_message: str,
        conversation_id: str,
        user_context: Optional[Dict] = None
    ) -> List[Dict[str, str]]:
        """Build the message array for OpenAI API."""
        
        # System prompt for Pfadi AI Assistant
        system_prompt = self._get_system_prompt(user_context)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (limit to last 10 exchanges)
        if conversation_id in self.conversation_memory:
            history = self.conversation_memory[conversation_id][-20:]  # Last 20 messages
            messages.extend(history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _get_system_prompt(self, user_context: Optional[Dict] = None) -> str:
        """Generate the system prompt for the Pfadi AI Assistant."""
        
        base_prompt = """Du bist der Pfadi AI Assistent, ein hilfsreicher KI-Assistent für Pfadfinderleiter:innen in Österreich.

DEINE ROLLE:
- Unterstütze bei der Planung von Heimstunden und Lagern für Guides und Späher (10-13 Jahre)
- Helfe beim Finden passender Spiele und Aktivitäten
- Beantworte Fragen zum Pfadfinderwissen, Gesetzen und Traditionen
- Gib pädagogische Ratschläge für die Altersgruppe 10-13 Jahre
- Sei authentisch pfadfinderisch und verwende entsprechende Begriffe

VERFÜGBARE FUNKTIONEN:
- search_games: Suche nach Spielen und Aktivitäten
- create_heimstunde_plan: Erstelle strukturierte Heimstundenpläne
- get_pfadfinder_knowledge: Beantworte Pfadfinderfragen

VERHALTEN:
- Sei freundlich, ermutigend und hilfsbereit
- Verwende die pfadfinderische Sprache ("Gut Pfad!", "Leiter:in", etc.)
- Biete konkrete, umsetzbare Vorschläge
- Frage nach, wenn wichtige Informationen fehlen
- Nutze die verfügbaren Funktionen, wenn passend
- Erkläre komplexe Konzepte altersgerecht

KONTEXT: Du hilfst bei der Arbeit mit Guides und Spähern (10-13 Jahre) in Niederösterreich und Wien."""

        if user_context:
            context_info = []
            if user_context.get("name"):
                context_info.append(f"Name: {user_context['name']}")
            if user_context.get("group"):
                context_info.append(f"Gruppe: {user_context['group']}")
            if user_context.get("experience_level"):
                context_info.append(f"Erfahrung: {user_context['experience_level']}")
            
            if context_info:
                base_prompt += f"\n\nBENUTZER-KONTEXT:\n{chr(10).join(context_info)}"
        
        return base_prompt
    
    async def _get_ai_response(
        self,
        messages: List[Dict[str, str]], 
        conversation_id: str
    ) -> Dict[str, Any]:
        """Get response from Azure OpenAI with function calling."""
        
        # Make API call with function definitions
        response = await azure_openai_service.chat_completion(
            messages=messages,
            temperature=0.7,
            functions=list(self.AVAILABLE_FUNCTIONS.values())
        )
        
        # Handle function calls
        if response.get("function_call"):
            function_result = await self._execute_function_call(response["function_call"])
            
            # Add function call and result to conversation
            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": response["function_call"]
            })
            messages.append({
                "role": "function",
                "name": response["function_call"]["name"],
                "content": json.dumps(function_result, ensure_ascii=False)
            })
            
            # Get final response incorporating function result
            final_response = await azure_openai_service.chat_completion(
                messages=messages,
                temperature=0.7
            )
            
            final_response["function_data"] = function_result
            return final_response
        
        return response
    
    async def _execute_function_call(self, function_call: Dict[str, str]) -> Dict[str, Any]:
        """Execute a function call and return the result."""
        
        function_name = function_call["name"]
        try:
            arguments = json.loads(function_call["arguments"])
        except json.JSONDecodeError:
            return {"error": "Invalid function arguments"}
        
        logger.info("Executing function call", function=function_name, arguments=arguments)
        
        if function_name == "search_games":
            return await self._search_games(**arguments)
        elif function_name == "create_heimstunde_plan":
            return await self._create_heimstunde_plan(**arguments)
        elif function_name == "get_pfadfinder_knowledge":
            return await self._get_pfadfinder_knowledge(**arguments)
        else:
            return {"error": f"Unknown function: {function_name}"}
    
    async def _search_games(self, query: str, **filters) -> Dict[str, Any]:
        """Mock implementation of game search."""
        # TODO: Integrate with actual game search service
        return {
            "games": [
                {
                    "name": "Vertrauenskreis",
                    "description": "Spiel zum Aufbau von Vertrauen in der Gruppe",
                    "duration_minutes": 15,
                    "participants": "8-15",
                    "location": "both",
                    "tags": ["vertrauen", "teambuilding"]
                }
            ],
            "query": query,
            "filters_applied": filters,
            "total_found": 1
        }
    
    async def _create_heimstunde_plan(self, **plan_data) -> Dict[str, Any]:
        """Mock implementation of heimstunde planning."""
        # TODO: Integrate with actual planning service
        return {
            "plan_id": str(uuid.uuid4()),
            "title": f"Heimstunde: {plan_data.get('theme', 'Allgemein')}",
            "duration": plan_data.get("duration", 90),
            "structure": [
                {"time": "19:00", "activity": "Begrüßung", "duration": 10},
                {"time": "19:10", "activity": "Hauptaktivität", "duration": 50},
                {"time": "20:00", "activity": "Reflexion", "duration": 20},
                {"time": "20:20", "activity": "Abschluss", "duration": 10}
            ],
            "materials": ["Je nach gewählten Aktivitäten"],
            "notes": "Plan an Gruppengröße anpassen"
        }
    
    async def _get_pfadfinder_knowledge(self, question: str, age_appropriate: bool = False) -> Dict[str, Any]:
        """Mock implementation of Pfadfinder knowledge."""
        # TODO: Integrate with RAG system and knowledge base
        knowledge_responses = {
            "pfadfindergesetze": "Die Pfadfindergesetze sind die Grundregeln unseres Zusammenlebens...",
            "allzeit bereit": "'Allzeit bereit' ist unser Wahlspruch und bedeutet...",
            "pfadfindergruß": "Der Pfadfindergruß wird mit drei Fingern gemacht..."
        }
        
        # Simple keyword matching for demo
        response = "Das ist eine interessante Frage zum Pfadfinderwissen. Für detaillierte Antworten benötige ich Zugang zur Wissensdatenbank."
        for keyword, answer in knowledge_responses.items():
            if keyword in question.lower():
                response = answer
                break
        
        return {
            "answer": response,
            "sources": ["Pfadfinder Grundlagen"],
            "age_appropriate": age_appropriate
        }
    
    def _get_fallback_response(self, user_message: str) -> Dict[str, Any]:
        """Generate fallback response when AI is not available."""
        return azure_openai_service._get_mock_response(user_message)
    
    def _update_conversation_memory(
        self,
        conversation_id: str,
        user_message: str,
        response: Dict[str, Any]
    ) -> None:
        """Update conversation memory with the latest exchange."""
        
        if conversation_id not in self.conversation_memory:
            self.conversation_memory[conversation_id] = []
        
        # Add user message
        self.conversation_memory[conversation_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Add assistant response
        self.conversation_memory[conversation_id].append({
            "role": "assistant", 
            "content": response.get("message", "")
        })
        
        # Keep only last 50 messages to prevent memory issues
        if len(self.conversation_memory[conversation_id]) > 50:
            self.conversation_memory[conversation_id] = self.conversation_memory[conversation_id][-50:]
    
    def _generate_suggested_actions(
        self,
        response: Dict[str, Any],
        user_message: str
    ) -> List[Dict[str, Any]]:
        """Generate suggested follow-up actions for the user."""
        
        actions = []
        
        # If function data is present, suggest related actions
        if response.get("function_data"):
            data = response["function_data"]
            
            if "games" in data:
                actions.extend([
                    {
                        "text": "📋 Heimstunde mit diesen Spielen planen",
                        "action": "create_plan",
                        "data": {"suggested_games": data["games"]}
                    },
                    {
                        "text": "🔍 Ähnliche Spiele suchen",
                        "action": "search_similar",
                        "data": {"reference_games": data["games"][:2]}
                    }
                ])
            
            if "plan_id" in data:
                actions.extend([
                    {
                        "text": "📄 Plan als PDF exportieren",
                        "action": "export_plan",
                        "data": {"plan_id": data["plan_id"]}
                    },
                    {
                        "text": "✏️ Plan anpassen",
                        "action": "modify_plan", 
                        "data": {"plan_id": data["plan_id"]}
                    }
                ])
        
        # General actions based on message content
        message_lower = user_message.lower()
        
        if not actions:  # Only add general actions if no specific ones
            if any(word in message_lower for word in ["spiel", "aktivität"]):
                actions.append({
                    "text": "🎯 Spiele suchen",
                    "action": "search_games",
                    "data": {}
                })
            
            actions.extend([
                {
                    "text": "📅 Heimstunde planen",
                    "action": "plan_heimstunde",
                    "data": {}
                },
                {
                    "text": "❓ Pfadfinderfrage stellen",
                    "action": "ask_knowledge",
                    "data": {}
                }
            ])
        
        return actions[:4]  # Limit to 4 suggestions
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a given conversation ID."""
        return self.conversation_memory.get(conversation_id, [])
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history for a given conversation ID."""
        if conversation_id in self.conversation_memory:
            del self.conversation_memory[conversation_id]
            return True
        return False


# Global service instance
pfadi_chat_service = PfadiChatService()