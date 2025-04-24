from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
from ..dependencies import get_world_or_404 # Použijeme jednodušší závislost

router = APIRouter()

# Helper dependency to get event and check world match
async def get_event_and_verify_world(
    event_id: int = Path(..., description="ID události"),
    world: models.World = Depends(get_world_or_404), # Použijeme jednodušší závislost
    db: Session = Depends(get_db),
) -> models.Event:
    db_event = crud.get_event(db, event_id=event_id)
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if db_event.world_id != world.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Event does not belong to this world"
        )
    # TODO: Ověřit oprávnění uživatele ke světu zde?
    return db_event

@router.post(
    "/", 
    response_model=schemas.Event, 
    status_code=status.HTTP_201_CREATED, 
    summary="Vytvořit novou událost ve světě"
)
def create_event(
    *, 
    event_in: schemas.EventCreate,
    world: models.World = Depends(get_world_or_404), # Použijeme jednodušší závislost
    db: Session = Depends(get_db),
    # TODO: Přidat kontrolu oprávnění (GM/Owner?) pro vytváření
    current_user: models.User = Depends(get_current_user) # Zatím jen ověření přihlášení
):
    """Vytvoří novou událost v rámci specifikovaného světa."""
    # TODO: Ověřit oprávnění uživatele k vytváření eventů ve světě
    db_event = crud.create_event(db=db, event_in=event_in, world_id=world.id)
    return db_event

@router.get("/", response_model=List[schemas.Event], summary="Získat události světa")
def read_events(
    *, 
    world: models.World = Depends(get_world_or_404), # Použijeme jednodušší závislost
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user) # Zatím jen ověření přihlášení
):
    """Získá seznam všech událostí v rámci specifikovaného světa."""
    # TODO: Ověřit oprávnění uživatele ke čtení eventů ve světě
    events = crud.get_events_by_world(db=db, world_id=world.id, skip=skip, limit=limit)
    return events

@router.get("/{event_id}", response_model=schemas.Event, summary="Získat detail události")
def read_event(
    *, 
    db_event: models.Event = Depends(get_event_and_verify_world), # Ověří existenci a příslušnost ke světu
    current_user: models.User = Depends(get_current_user) # Ověří přihlášení
):
    """Získá detail konkrétní události."""
    # TODO: Ověřit oprávnění uživatele ke čtení tohoto eventu
    return db_event

@router.put("/{event_id}", response_model=schemas.Event, summary="Aktualizovat událost")
def update_event(
    *, 
    event_in: schemas.EventUpdate,
    db_event: models.Event = Depends(get_event_and_verify_world), # Ověří existenci a příslušnost
    db: Session = Depends(get_db),
    # TODO: Přidat kontrolu oprávnění (GM/Owner?) pro úpravu
    current_user: models.User = Depends(get_current_user) # Zatím jen ověření přihlášení
):
    """Aktualizuje konkrétní událost."""
    # TODO: Ověřit oprávnění uživatele k úpravě tohoto eventu
    updated_event = crud.update_event(db=db, db_event=db_event, event_in=event_in)
    return updated_event

@router.delete("/{event_id}", response_model=schemas.Event, summary="Smazat událost")
def delete_event(
    *, 
    db_event: models.Event = Depends(get_event_and_verify_world), # Ověří existenci a příslušnost
    db: Session = Depends(get_db),
    # TODO: Přidat kontrolu oprávnění (GM/Owner?) pro smazání
    current_user: models.User = Depends(get_current_user) # Zatím jen ověření přihlášení
):
    """Smaže konkrétní událost."""
    # TODO: Ověřit oprávnění uživatele ke smazání tohoto eventu
    deleted_event = crud.delete_event(db=db, db_event=db_event)
    # TODO: Zvážit vrácení 204 No Content místo smazaného objektu
    return deleted_event 