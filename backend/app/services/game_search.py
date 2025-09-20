"""
Game search service with semantic search capabilities.
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
import structlog

from app.services.azure_openai import azure_openai_service
from app.core.config import settings

logger = structlog.get_logger()


class GameSearchService:
    """Service for intelligent game search with semantic capabilities."""
    
    def __init__(self):
        """Initialize the game search service."""
        # Mock game database - in production this would be from a real database
        self.mock_games = [
            {
                "gameId": "game_001",
                "name": "Vertrauenskreis",
                "description": "Die Teilnehmer stehen im Kreis und lassen sich rückwärts fallen, vertrauen darauf, dass sie aufgefangen werden. Dieses Spiel fördert Vertrauen und Gruppenzusammenhalt.",
                "materials": ["Keine besonderen Materialien"],
                "durationMinutes": 15,
                "minParticipants": 8,
                "maxParticipants": 15,
                "ageGroup": "10-13",
                "location": "both",
                "weatherDependency": "low",
                "tags": ["vertrauen", "teambuilding", "kreis", "sozial"],
                "pedagogicalValue": "Fördert Vertrauen und Gruppenzusammenhalt",
                "sourceUrl": None,
                "rating": 4.2,
                "embedding": None  # Will be generated on first use
            },
            {
                "gameId": "game_002",
                "name": "Capture the Flag",
                "description": "Zwei Teams versuchen die Fahne des anderen Teams zu erobern und in ihr eigenes Territorium zu bringen. Strategisches Teamspiel für größere Gruppen.",
                "materials": ["2 Fahnen", "Markierungen für Spielfeld", "Bänder oder Tücher"],
                "durationMinutes": 30,
                "minParticipants": 10,
                "maxParticipants": 20,
                "ageGroup": "10-13",
                "location": "outdoor",
                "weatherDependency": "medium",
                "tags": ["strategie", "team", "bewegung", "wettkampf", "outdoor"],
                "pedagogicalValue": "Fördert strategisches Denken und Teamwork",
                "sourceUrl": None,
                "rating": 4.7,
                "embedding": None
            },
            {
                "gameId": "game_003",
                "name": "Blindes Vertrauen Parcours",
                "description": "Ein Teilnehmer wird durch einen Parcours geführt, während er die Augen verbunden hat. Der Partner gibt nur verbale Anweisungen.",
                "materials": ["Augenbinden", "Hindernisse", "Seile", "Gegenstände für Parcours"],
                "durationMinutes": 20,
                "minParticipants": 6,
                "maxParticipants": 16,
                "ageGroup": "10-13",
                "location": "both",
                "weatherDependency": "low",
                "tags": ["vertrauen", "kommunikation", "parcours", "teambuilding"],
                "pedagogicalValue": "Stärkt Vertrauen und Kommunikationsfähigkeiten",
                "sourceUrl": None,
                "rating": 4.0,
                "embedding": None
            },
            {
                "gameId": "game_004", 
                "name": "Geschichten erfinden",
                "description": "Die Gruppe erfindet gemeinsam eine Geschichte, wobei jeder Teilnehmer einen Satz beiträgt. Fördert Kreativität und Zuhören.",
                "materials": ["Eventuell Papier und Stifte"],
                "durationMinutes": 25,
                "minParticipants": 5,
                "maxParticipants": 12,
                "ageGroup": "10-13",
                "location": "indoor",
                "weatherDependency": "low",
                "tags": ["kreativität", "sprache", "zuhören", "ruhig", "indoor"],
                "pedagogicalValue": "Entwickelt Kreativität und Sprachfähigkeiten",
                "sourceUrl": None,
                "rating": 3.8,
                "embedding": None
            },
            {
                "gameId": "game_005",
                "name": "Menschliche Knoten",
                "description": "Die Teilnehmer stellen sich in einen Kreis, greifen sich an den Händen und bilden einen 'Knoten', den sie gemeinsam lösen müssen.",
                "materials": ["Keine Materialien erforderlich"],
                "durationMinutes": 15,
                "minParticipants": 6,
                "maxParticipants": 12,
                "ageGroup": "10-13", 
                "location": "both",
                "weatherDependency": "low",
                "tags": ["problemlösung", "teamwork", "kooperation", "körperkontakt"],
                "pedagogicalValue": "Fördert Problemlösungskompetenzen und Zusammenarbeit",
                "sourceUrl": None,
                "rating": 4.1,
                "embedding": None
            }
        ]
    
    async def search_games(
        self,
        query: Optional[str] = None,
        duration_max: Optional[int] = None,
        participant_count: Optional[int] = None,
        location: Optional[str] = None,
        age_group: Optional[str] = None,
        tags: Optional[List[str]] = None,
        use_semantic_search: bool = True,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for games using both keyword filtering and semantic search.
        
        Args:
            query: Search query for semantic search
            duration_max: Maximum duration in minutes
            participant_count: Number of participants
            location: indoor, outdoor, or both
            age_group: Age group (e.g., "10-13")
            tags: List of tags to filter by
            use_semantic_search: Whether to use semantic search
            limit: Maximum number of results
            
        Returns:
            Dict with games, scores, and metadata
        """
        
        logger.info(
            "Starting game search",
            query=query,
            duration_max=duration_max,
            participant_count=participant_count,
            location=location,
            use_semantic=use_semantic_search
        )
        
        # Start with all games
        candidate_games = self.mock_games.copy()
        
        # Apply keyword filters first
        filtered_games = self._apply_keyword_filters(
            candidate_games,
            duration_max=duration_max,
            participant_count=participant_count,
            location=location,
            age_group=age_group,
            tags=tags
        )
        
        logger.info(f"After keyword filtering: {len(filtered_games)} games")
        
        # Apply semantic search if query provided and service available
        if query and use_semantic_search and azure_openai_service.is_available():
            try:
                semantic_results = await self._semantic_search(query, filtered_games)
                final_results = semantic_results[:limit]
                search_type = "semantic"
            except Exception as e:
                logger.warning("Semantic search failed, falling back to keyword search", error=str(e))
                final_results = filtered_games[:limit]
                search_type = "keyword_fallback"
        else:
            # Simple text matching for query
            if query:
                query_lower = query.lower()
                text_matched = []
                for game in filtered_games:
                    score = self._calculate_text_match_score(game, query_lower)
                    if score > 0:
                        game_copy = game.copy()
                        game_copy["search_score"] = score
                        text_matched.append(game_copy)
                
                # Sort by score
                text_matched.sort(key=lambda x: x["search_score"], reverse=True)
                final_results = text_matched[:limit]
                search_type = "text_match"
            else:
                final_results = filtered_games[:limit]
                search_type = "filter_only"
        
        logger.info(
            "Game search completed",
            results_count=len(final_results),
            search_type=search_type
        )
        
        return {
            "games": final_results,
            "total_found": len(final_results),
            "search_type": search_type,
            "query_processed": query,
            "filters_applied": {
                "duration_max": duration_max,
                "participant_count": participant_count,
                "location": location,
                "age_group": age_group,
                "tags": tags
            }
        }
    
    def _apply_keyword_filters(
        self,
        games: List[Dict],
        duration_max: Optional[int] = None,
        participant_count: Optional[int] = None,
        location: Optional[str] = None,
        age_group: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict]:
        """Apply keyword-based filters to games."""
        
        filtered = []
        
        for game in games:
            # Duration filter
            if duration_max and game["durationMinutes"] > duration_max:
                continue
            
            # Participant count filter
            if participant_count:
                if (game["minParticipants"] > participant_count or 
                    game["maxParticipants"] < participant_count):
                    continue
            
            # Location filter
            if location and location != "both":
                if game["location"] != "both" and game["location"] != location:
                    continue
            
            # Age group filter
            if age_group and game["ageGroup"] != age_group:
                continue
            
            # Tags filter
            if tags:
                game_tags = set(game["tags"])
                required_tags = set(tags)
                if not required_tags.intersection(game_tags):
                    continue
            
            filtered.append(game)
        
        return filtered
    
    async def _semantic_search(
        self, 
        query: str, 
        games: List[Dict]
    ) -> List[Dict]:
        """Perform semantic search using embeddings."""
        
        # Generate query embedding
        query_embedding = await azure_openai_service.generate_embedding(query)
        
        # Generate game embeddings if not cached
        games_with_embeddings = []
        for game in games:
            if game["embedding"] is None:
                # Create search text for embedding
                search_text = self._create_game_search_text(game)
                game["embedding"] = await azure_openai_service.generate_embedding(search_text)
            
            games_with_embeddings.append(game)
        
        # Calculate similarity scores
        scored_games = []
        for game in games_with_embeddings:
            similarity = self._cosine_similarity(query_embedding, game["embedding"])
            game_copy = game.copy()
            game_copy["semantic_score"] = similarity
            scored_games.append(game_copy)
        
        # Sort by similarity score
        scored_games.sort(key=lambda x: x["semantic_score"], reverse=True)
        
        return scored_games
    
    def _create_game_search_text(self, game: Dict) -> str:
        """Create a comprehensive text representation for embedding generation."""
        
        search_parts = [
            game["name"],
            game["description"],
            game["pedagogicalValue"],
            " ".join(game["tags"]),
            f"Dauer: {game['durationMinutes']} Minuten",
            f"Teilnehmer: {game['minParticipants']}-{game['maxParticipants']}",
            f"Ort: {game['location']}",
            f"Materialien: {', '.join(game['materials'])}"
        ]
        
        return " ".join(search_parts)
    
    def _calculate_text_match_score(self, game: Dict, query_lower: str) -> float:
        """Calculate text matching score for keyword search."""
        
        score = 0.0
        
        # Name match (highest weight)
        if query_lower in game["name"].lower():
            score += 3.0
        
        # Description match
        if query_lower in game["description"].lower():
            score += 2.0
        
        # Tags match
        for tag in game["tags"]:
            if query_lower in tag.lower():
                score += 1.5
        
        # Pedagogical value match
        if query_lower in game["pedagogicalValue"].lower():
            score += 1.0
        
        # Materials match
        for material in game["materials"]:
            if query_lower in material.lower():
                score += 0.5
        
        return score
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    async def get_game_by_id(self, game_id: str) -> Optional[Dict]:
        """Get a specific game by ID."""
        
        for game in self.mock_games:
            if game["gameId"] == game_id:
                return game.copy()
        
        return None
    
    async def get_similar_games(
        self, 
        game_id: str, 
        limit: int = 5
    ) -> List[Dict]:
        """Find games similar to a given game."""
        
        target_game = await self.get_game_by_id(game_id)
        if not target_game:
            return []
        
        # Use the game's description and tags as query
        query = f"{target_game['description']} {' '.join(target_game['tags'])}"
        
        # Search for similar games (exclude the target game)
        search_result = await self.search_games(
            query=query,
            use_semantic_search=True,
            limit=limit + 1
        )
        
        # Filter out the original game
        similar_games = [
            game for game in search_result["games"]
            if game["gameId"] != game_id
        ]
        
        return similar_games[:limit]


# Global service instance
game_search_service = GameSearchService()