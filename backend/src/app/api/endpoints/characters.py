from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Character)
def create_character(
    *,
    db: Session = Depends(get_db),
    character_in: schemas.CharacterCreate,
    current_user: models.User = Depends(get_current_user)
):
    """
    Create new character. User must be a member of the world.
    """
    # CRUD funkce create_character nyní ověřuje členství ve světě
    character = crud.create_character(db=db, character_in=character_in, user_id=current_user.id)
    if not character:
        # CRUD vrátí None, pokud uživatel není členem světa nebo svět neexistuje
        raise HTTPException(status_code=403, detail="World not found or user is not a member")
    return character

@router.get("/", response_model=List[schemas.Character])
def read_characters(
    db: Session = Depends(get_db),
    world_id: Optional[int] = None, # Allow filtering by world
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve characters owned by the current user.
    Can be filtered by world_id.
    """
    if world_id:
        # Zde není potřeba ověřovat členství ve světě explicitně,
        # protože get_characters_by_world vrací jen postavy patřící current_user,
        # které mohou existovat jen ve světě, jehož je členem (ověřeno při create_character).
        characters = crud.get_characters_by_world(db, world_id=world_id, user_id=current_user.id, skip=skip, limit=limit)
    else:
        characters = crud.get_characters_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return characters

@router.get("/{character_id}", response_model=schemas.Character)
def read_character(
    *,
    db: Session = Depends(get_db),
    character_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """
    Get character by ID.
    """
    character = crud.get_character(db, character_id=character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return character

@router.put("/{character_id}", response_model=schemas.Character)
def update_character(
    *,
    db: Session = Depends(get_db),
    character_id: int,
    character_in: schemas.CharacterUpdate,
    current_user: models.User = Depends(get_current_user)
):
    """
    Update a character.
    """
    db_character = crud.get_character(db, character_id=character_id)
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")
    if db_character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    character = crud.update_character(db=db, db_character=db_character, character_in=character_in)
    return character

@router.delete("/{character_id}", response_model=schemas.Character)
def delete_character(
    *,
    db: Session = Depends(get_db),
    character_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a character.
    """
    db_character = crud.get_character(db, character_id=character_id)
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")
    if db_character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    character = crud.delete_character(db=db, db_character=db_character)
    return character 