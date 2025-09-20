"""
Game search and management endpoints.
"""

import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import structlog

from app.core.config import settings
from app.services.game_search import game_search_service

logger = structlog.get_logger()
router = APIRouter()


class GameFilters(BaseModel):
    query: Optional[str] = None
    duration_max: Optional[int] = None
    participant_count: Optional[int] = None
    location: Optional[str] = None
    age_group: Optional[str] = None
    tags: Optional[List[str]] = None


class Game(BaseModel):
    gameId: str
    name: str
    description: str
    materials: List[str]
    durationMinutes: int
    minParticipants: int
    maxParticipants: int
    ageGroup: str
    location: str
    weatherDependency: str
    tags: List[str]
    pedagogicalValue: str
    sourceUrl: Optional[str] = None
    rating: Optional[float] = None
    semantic_score: Optional[float] = None
    search_score: Optional[float] = None


class GameSearchResponse(BaseModel):
    games: List[Game]
    total_found: int
    query_time_ms: int
    search_type: str
    azure_openai_used: bool


@router.get("/search", response_model=GameSearchResponse)
async def search_games(
    q: Optional[str] = Query(None, description="Search query for semantic search"),
    duration_max: Optional[int] = Query(None, description="Maximum duration in minutes"),
    participant_count: Optional[int] = Query(None, description="Number of participants"),
    location: Optional[str] = Query(None, description="indoor, outdoor, or both"),
    age_group: Optional[str] = Query("10-13", description="Age group"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    semantic: bool = Query(True, description="Use semantic search with Azure OpenAI"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return")
):
    """Search for games using advanced semantic search and filtering."""
    
    if not settings.ENABLE_GAME_SEARCH:
        raise HTTPException(status_code=501, detail="Game search feature is disabled")
    
    start_time = time.time()
    
    # Parse tags if provided
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    logger.info(
        "Processing game search request",
        query=q,
        semantic_enabled=semantic,
        filters={
            "duration_max": duration_max,
            "participant_count": participant_count,
            "location": location,
            "tags": tag_list
        }
    )
    
    try:
        # Use our game search service
        search_result = await game_search_service.search_games(
            query=q,
            duration_max=duration_max,
            participant_count=participant_count,
            location=location,
            age_group=age_group,
            tags=tag_list,
            use_semantic_search=semantic,
            limit=limit
        )
        
        # Convert to Game objects
        games = []
        for game_data in search_result["games"]:
            # Remove embedding from response
            game_dict = {k: v for k, v in game_data.items() if k != "embedding"}
            games.append(Game(**game_dict))
        
        query_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "Game search completed",
            results_count=len(games),
            query_time_ms=query_time_ms,
            search_type=search_result["search_type"]
        )
        
        from app.services.azure_openai import azure_openai_service
        
        return GameSearchResponse(
            games=games,
            total_found=search_result["total_found"],
            query_time_ms=query_time_ms,
            search_type=search_result["search_type"],
            azure_openai_used=azure_openai_service.is_available() and semantic
        )
        
    except Exception as e:
        logger.error("Error during game search", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Fehler bei der Spielesuche. Bitte versuche es erneut."
        )
    
    return GameSearchResponse(
        games=filtered_games[:limit],
        total_found=len(filtered_games),
        query_time_ms=42  # Mock query time
    )


@router.get("/{game_id}", response_model=Game)
async def get_game(game_id: str):
    """Get a specific game by ID."""
    
    # TODO: Implement actual game retrieval
    # For now, return a mock game or 404
    if game_id == "game_001":
        return Game(
            gameId="game_001",
            name="Vertrauenskreis",
            description="Die Teilnehmer stehen im Kreis und lassen sich rückwärts fallen, vertrauen darauf, dass sie aufgefangen werden.",
            materials=["Keine besonderen Materialien"],
            durationMinutes=15,
            minParticipants=8,
            maxParticipants=15,
            ageGroup="10-13",
            location="both",
            weatherDependency="low",
            tags=["vertrauen", "teambuilding", "kreis"],
            pedagogicalValue="Fördert Vertrauen und Gruppenzusammenhalt",
            rating=4.2
        )
    
    raise HTTPException(status_code=404, detail="Game not found")


@router.get("/", response_model=GameSearchResponse)
async def list_games(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List all games with pagination."""
    
    # TODO: Implement actual game listing
    return await search_games(limit=limit)