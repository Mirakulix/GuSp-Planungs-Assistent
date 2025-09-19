"""
Planning endpoints for creating and managing activity plans.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, date
import uuid

from app.core.config import settings

router = APIRouter()


class PedagogicalGoal(BaseModel):
    type: str  # "teambuilding", "leadership", "creativity", etc.
    description: str


class ScheduleItem(BaseModel):
    start_time: str  # Format: "HH:MM"
    duration: int    # Minutes
    activity_name: str
    activity_type: str  # "game", "discussion", "craft", etc.
    description: str
    materials: List[str] = []
    notes: Optional[str] = None


class PlanningRequest(BaseModel):
    title: Optional[str] = None
    date: date
    duration: int  # Total duration in minutes
    participant_count: int
    age_group: str = "10-13"
    theme: Optional[str] = None
    location: str = "indoor"  # "indoor", "outdoor", "flexible"
    pedagogical_goals: List[PedagogicalGoal] = []
    special_requirements: Optional[str] = None


class ActivityPlan(BaseModel):
    plan_id: str
    title: str
    date: date
    duration: int
    participant_count: int
    age_group: str
    theme: Optional[str]
    location: str
    pedagogical_goals: List[PedagogicalGoal]
    schedule: List[ScheduleItem]
    material_list: List[str]
    preparation_notes: List[str]
    created_at: datetime
    updated_at: datetime


class PlanSuggestion(BaseModel):
    suggested_schedule: List[ScheduleItem]
    alternative_activities: List[dict]
    estimated_preparation_time: int  # Minutes
    difficulty_level: str  # "easy", "medium", "challenging"


@router.post("/heimstunde", response_model=ActivityPlan)
async def create_heimstunde_plan(request: PlanningRequest):
    """Create a new Heimstunde (troop meeting) plan."""
    
    if not settings.ENABLE_PLANNING:
        raise HTTPException(status_code=501, detail="Planning feature is disabled")
    
    plan_id = str(uuid.uuid4())
    
    # TODO: Implement actual AI-powered planning logic
    # For now, create a mock plan
    
    # Generate a simple schedule based on duration
    schedule = []
    current_time = "19:00"  # Default start time
    remaining_duration = request.duration
    
    # Opening (10 minutes)
    if remaining_duration >= 10:
        schedule.append(ScheduleItem(
            start_time=current_time,
            duration=10,
            activity_name="Begrüßung und Eröffnung",
            activity_type="opening",
            description="Gemeinsame Begrüßung, kurze Runde zum Befinden",
            materials=["Kluft", "eventuell Fahne"]
        ))
        remaining_duration -= 10
        current_time = _add_minutes_to_time(current_time, 10)
    
    # Main activities (60-70% of remaining time)
    main_activity_time = int(remaining_duration * 0.7)
    if main_activity_time >= 15:
        activity_name = "Teambuilding-Spiel"
        activity_description = "Spiel zur Stärkung des Gruppengefühls"
        
        if request.theme:
            activity_name = f"Aktivität zum Thema '{request.theme}'"
            activity_description = f"Kreative Aktivität passend zum Thema {request.theme}"
        
        schedule.append(ScheduleItem(
            start_time=current_time,
            duration=main_activity_time,
            activity_name=activity_name,
            activity_type="main_activity",
            description=activity_description,
            materials=["Je nach gewähltem Spiel"],
            notes="Spiel an Gruppengröße anpassen"
        ))
        remaining_duration -= main_activity_time
        current_time = _add_minutes_to_time(current_time, main_activity_time)
    
    # Reflection/discussion (15-20% of remaining time)
    if remaining_duration >= 10:
        reflection_time = min(remaining_duration - 5, int(remaining_duration * 0.7))
        schedule.append(ScheduleItem(
            start_time=current_time,
            duration=reflection_time,
            activity_name="Reflexion und Gespräch",
            activity_type="reflection",
            description="Gemeinsame Reflexion über die Aktivitäten und Erfahrungen",
            materials=["Sitzkreis"]
        ))
        remaining_duration -= reflection_time
        current_time = _add_minutes_to_time(current_time, reflection_time)
    
    # Closing
    if remaining_duration >= 5:
        schedule.append(ScheduleItem(
            start_time=current_time,
            duration=remaining_duration,
            activity_name="Abschluss",
            activity_type="closing",
            description="Gemeinsamer Abschluss, Termine und Verabschiedung",
            materials=[]
        ))
    
    # Aggregate materials
    all_materials = []
    for item in schedule:
        all_materials.extend(item.materials)
    unique_materials = list(set(all_materials))
    
    # Generate preparation notes
    preparation_notes = [
        "Raum/Platz entsprechend der geplanten Aktivitäten vorbereiten",
        "Alle Materialien im Voraus bereitlegen",
        f"Aktivitäten für {request.participant_count} Teilnehmer anpassen"
    ]
    
    if request.location == "outdoor":
        preparation_notes.append("Wetterbericht prüfen und Backup-Plan für schlechtes Wetter")
    
    plan = ActivityPlan(
        plan_id=plan_id,
        title=request.title or f"Heimstunde {request.date.strftime('%d.%m.%Y')}",
        date=request.date,
        duration=request.duration,
        participant_count=request.participant_count,
        age_group=request.age_group,
        theme=request.theme,
        location=request.location,
        pedagogical_goals=request.pedagogical_goals,
        schedule=schedule,
        material_list=unique_materials,
        preparation_notes=preparation_notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    return plan


@router.post("/heimstunde/suggestions", response_model=PlanSuggestion)
async def get_plan_suggestions(request: PlanningRequest):
    """Get AI-powered suggestions for a Heimstunde plan."""
    
    # TODO: Implement actual AI suggestion logic
    # For now, return mock suggestions
    
    suggested_schedule = [
        ScheduleItem(
            start_time="19:00",
            duration=10,
            activity_name="Energizer: Namen-Ball",
            activity_type="game",
            description="Schnelles Kennenlernspiel mit Ball",
            materials=["Softball"]
        ),
        ScheduleItem(
            start_time="19:10",
            duration=25,
            activity_name="Hauptaktivität: Vertrauensparcours",
            activity_type="team_activity", 
            description="Parcours mit verbundenen Augen zur Stärkung des Vertrauens",
            materials=["Augenbinden", "Hindernisse", "Seile"]
        ),
        ScheduleItem(
            start_time="19:35",
            duration=15,
            activity_name="Reflexionsrunde",
            activity_type="discussion",
            description="Gespräch über Vertrauen und Zusammenhalt",
            materials=["Sitzkreis"]
        )
    ]
    
    return PlanSuggestion(
        suggested_schedule=suggested_schedule,
        alternative_activities=[
            {"name": "Kooperationsspiele", "type": "alternative_main"},
            {"name": "Kreative Gestaltung", "type": "alternative_main"},
            {"name": "Outdoor-Aktivität", "type": "weather_alternative"}
        ],
        estimated_preparation_time=20,
        difficulty_level="medium"
    )


@router.get("/{plan_id}", response_model=ActivityPlan)
async def get_plan(plan_id: str):
    """Get a specific activity plan by ID."""
    
    # TODO: Implement actual plan retrieval from database
    raise HTTPException(status_code=404, detail="Plan not found")


@router.get("/", response_model=List[ActivityPlan])
async def list_plans(limit: int = 20, offset: int = 0):
    """List all activity plans with pagination."""
    
    # TODO: Implement actual plan listing from database
    return []


def _add_minutes_to_time(time_str: str, minutes: int) -> str:
    """Helper function to add minutes to a time string."""
    from datetime import datetime, timedelta
    
    time_obj = datetime.strptime(time_str, "%H:%M")
    new_time = time_obj + timedelta(minutes=minutes)
    return new_time.strftime("%H:%M")