"""
Power Map API routes
"""

from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from datetime import datetime

from subtext.models import (
    PowerMap,
    Person,
    Relationship,
    CreatePowerMapRequest,
    CreatePersonRequest,
    CreateRelationshipRequest,
)

router = APIRouter(tags=["power_map"])

# In-memory storage (will be replaced with database later)
power_maps: dict[str, PowerMap] = {}
people: dict[str, Person] = {}
relationships: dict[str, Relationship] = {}


@router.post("/power-maps", response_model=PowerMap)
async def create_power_map(request: CreatePowerMapRequest) -> PowerMap:
    """Create a new power map"""
    power_map = PowerMap(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        people=[],
        relationships=[],
    )
    power_maps[power_map.id] = power_map
    return power_map


@router.get("/power-maps", response_model=List[PowerMap])
async def list_power_maps() -> List[PowerMap]:
    """List all power maps"""
    return list(power_maps.values())


@router.get("/power-maps/{power_map_id}", response_model=PowerMap)
async def get_power_map(power_map_id: str) -> PowerMap:
    """Get a specific power map"""
    if power_map_id not in power_maps:
        raise HTTPException(status_code=404, detail="Power map not found")
    return power_maps[power_map_id]


@router.delete("/power-maps/{power_map_id}")
async def delete_power_map(power_map_id: str) -> dict:
    """Delete a power map"""
    if power_map_id not in power_maps:
        raise HTTPException(status_code=404, detail="Power map not found")
    del power_maps[power_map_id]
    return {"message": "Power map deleted"}


@router.post("/power-maps/{power_map_id}/people", response_model=Person)
async def add_person_to_map(power_map_id: str, request: CreatePersonRequest) -> Person:
    """Add a person to a power map"""
    if power_map_id not in power_maps:
        raise HTTPException(status_code=404, detail="Power map not found")

    person = Person(
        id=str(uuid.uuid4()),
        name=request.name,
        title=request.title,
        department=request.department,
        influence_level=request.influence_level,
        notes=request.notes,
    )

    people[person.id] = person
    power_maps[power_map_id].people.append(person)
    power_maps[power_map_id].updated_at = datetime.utcnow()

    return person


@router.get("/power-maps/{power_map_id}/people", response_model=List[Person])
async def list_people_in_map(power_map_id: str) -> List[Person]:
    """List all people in a power map"""
    if power_map_id not in power_maps:
        raise HTTPException(status_code=404, detail="Power map not found")
    return power_maps[power_map_id].people


@router.delete("/power-maps/{power_map_id}/people/{person_id}")
async def remove_person_from_map(power_map_id: str, person_id: str) -> dict:
    """Remove a person from a power map"""
    if power_map_id not in power_maps:
        raise HTTPException(status_code=404, detail="Power map not found")

    power_map = power_maps[power_map_id]
    power_map.people = [p for p in power_map.people if p.id != person_id]
    power_map.updated_at = datetime.utcnow()

    if person_id in people:
        del people[person_id]

    return {"message": "Person removed from power map"}


@router.post("/power-maps/{power_map_id}/relationships", response_model=Relationship)
async def add_relationship_to_map(
    power_map_id: str, request: CreateRelationshipRequest
) -> Relationship:
    """Add a relationship to a power map"""
    if power_map_id not in power_maps:
        raise HTTPException(status_code=404, detail="Power map not found")

    # Verify both people exist in the map
    power_map = power_maps[power_map_id]
    person_ids = {p.id for p in power_map.people}

    if request.from_person_id not in person_ids:
        raise HTTPException(status_code=404, detail="From person not found in map")
    if request.to_person_id not in person_ids:
        raise HTTPException(status_code=404, detail="To person not found in map")

    relationship = Relationship(
        id=str(uuid.uuid4()),
        from_person_id=request.from_person_id,
        to_person_id=request.to_person_id,
        relationship_type=request.relationship_type,
        strength=request.strength,
        notes=request.notes,
    )

    relationships[relationship.id] = relationship
    power_map.relationships.append(relationship)
    power_map.updated_at = datetime.utcnow()

    return relationship


@router.get("/power-maps/{power_map_id}/relationships", response_model=List[Relationship])
async def list_relationships_in_map(power_map_id: str) -> List[Relationship]:
    """List all relationships in a power map"""
    if power_map_id not in power_maps:
        raise HTTPException(status_code=404, detail="Power map not found")
    return power_maps[power_map_id].relationships


@router.delete("/power-maps/{power_map_id}/relationships/{relationship_id}")
async def remove_relationship_from_map(power_map_id: str, relationship_id: str) -> dict:
    """Remove a relationship from a power map"""
    if power_map_id not in power_maps:
        raise HTTPException(status_code=404, detail="Power map not found")

    power_map = power_maps[power_map_id]
    power_map.relationships = [r for r in power_map.relationships if r.id != relationship_id]
    power_map.updated_at = datetime.utcnow()

    if relationship_id in relationships:
        del relationships[relationship_id]

    return {"message": "Relationship removed from power map"}
