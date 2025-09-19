"""
Game search and management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.config import settings

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


class GameSearchResponse(BaseModel):
    games: List[Game]
    total_found: int
    query_time_ms: int


@router.get("/search", response_model=GameSearchResponse)
async def search_games(
    q: Optional[str] = Query(None, description="Search query"),
    duration_max: Optional[int] = Query(None, description="Maximum duration in minutes"),
    participant_count: Optional[int] = Query(None, description="Number of participants"),
    location: Optional[str] = Query(None, description="indoor, outdoor, or both"),
    age_group: Optional[str] = Query("10-13", description="Age group"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return")
):
    """Search for games with various filters."""
    
    if not settings.ENABLE_GAME_SEARCH:
        raise HTTPException(status_code=501, detail="Game search feature is disabled")
    
    # Parse tags if provided
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    filters = GameFilters(
        query=q,
        duration_max=duration_max,
        participant_count=participant_count,
        location=location,
        age_group=age_group,
        tags=tag_list
    )
    
    # TODO: Implement actual search logic
    # For now, return mock data
    mock_games = [
        Game(
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
        ),
        Game(
            gameId="game_002", 
            name="Capture the Flag",
            description="Zwei Teams versuchen die Fahne des anderen Teams zu erobern und in ihr eigenes Territorium zu bringen.",
            materials=["2 Fahnen", "Markierungen für Spielfeld"],
            durationMinutes=30,
            minParticipants=10,
            maxParticipants=20,
            ageGroup="10-13",
            location="outdoor",
            weatherDependency="medium",
            tags=["strategie", "team", "bewegung", "wettkampf"],
            pedagogicalValue="Fördert strategisches Denken und Teamwork",
            rating=4.7
        )
    ]
    
    # Filter mock games based on criteria
    filtered_games = []
    for game in mock_games:
        if filters.duration_max and game.durationMinutes > filters.duration_max:
            continue
        if filters.participant_count and (
            game.minParticipants > filters.participant_count or 
            game.maxParticipants < filters.participant_count
        ):
            continue
        if filters.location and filters.location != "both" and game.location != "both" and game.location != filters.location:
            continue
        if filters.query and filters.query.lower() not in game.name.lower() and filters.query.lower() not in game.description.lower():
            continue
        
        filtered_games.append(game)
    
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