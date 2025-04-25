from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
from ..dependencies import get_world_or_404, verify_world_owner

router = APIRouter()

# Závislost pro získání typu tagu charakteru a ověření příslušnosti ke světu
async def get_character_tag_type_from_world(
    tag_type_id: int = Path(..., description="ID typu tagu charakteru"),
    world: models.World = Depends(get_world_or_404),
    db: Session = Depends(get_db)
) -> models.CharacterTagType:
    db_tag_type = crud.get_character_tag_type(db, tag_type_id=tag_type_id)
    if not db_tag_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character tag type not found")
    if db_tag_type.world_id != world.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Character tag type does not belong to this world"
        )
    return db_tag_type

@router.post(
    "", 
    response_model=schemas.CharacterTagType, 
    status_code=status.HTTP_201_CREATED, 
    summary="Vytvořit nový typ tagu pro charaktery ve světě"
)
async def create_character_tag_type(
    *,
    world_id: int, # Přichází z prefixu
    tag_type_in: schemas.CharacterTagTypeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    _=Depends(verify_world_owner) # Ověření vlastníka světa
):
    """Vytvoří nový typ tagu pro charaktery v rámci specifikovaného světa. Vyžaduje vlastnictví světa."""
    # Ověření vlastníka světa je zajištěno závislostí verify_world_owner
    try:
        db_tag_type = crud.create_character_tag_type(db=db, tag_type_in=tag_type_in, world_id=world_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return db_tag_type

@router.get("", response_model=List[schemas.CharacterTagType], summary="Získat typy tagů charakterů světa")
def read_character_tag_types(
    *,
    world: models.World = Depends(get_world_or_404), # Ověří existenci světa a získá ho
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # TODO: Ověřit členství ve světě pro čtení? Nebo stačí být přihlášen?
    current_user: models.User = Depends(get_current_user) # Zatím jen ověření přihlášení
):
    """Získá seznam všech typů tagů pro charaktery v rámci specifikovaného světa."""
    tag_types = crud.get_character_tag_types_by_world(db=db, world_id=world.id, skip=skip, limit=limit)
    return tag_types

@router.put("/{tag_type_id}", response_model=schemas.CharacterTagType, summary="Aktualizovat typ tagu charakteru")
async def update_character_tag_type(
    *,
    world_id: int, # Přichází z prefixu, potřeba pro ověření vlastníka
    tag_type_id: int = Path(..., description="ID typu tagu charakteru"),
    tag_type_in: schemas.CharacterTagTypeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    _=Depends(verify_world_owner) # Ověření vlastníka světa
):
    """Aktualizuje konkrétní typ tagu charakteru. Vyžaduje vlastnictví světa."""
    # Ověření vlastníka světa je zajištěno závislostí verify_world_owner
    # Závislost get_world_or_404 je také implicitně volána přes verify_world_owner
    world = await get_world_or_404(world_id=world_id, db=db)
    db_tag_type = await get_character_tag_type_from_world(tag_type_id=tag_type_id, world=world, db=db)

    try:
        updated_tag_type = crud.update_character_tag_type(db=db, db_tag_type=db_tag_type, tag_type_in=tag_type_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return updated_tag_type

@router.delete("/{tag_type_id}", response_model=schemas.CharacterTagType, summary="Smazat typ tagu charakteru")
async def delete_character_tag_type(
    *,
    world_id: int, # Přichází z prefixu, potřeba pro ověření vlastníka
    tag_type_id: int = Path(..., description="ID typu tagu charakteru"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    _=Depends(verify_world_owner) # Ověření vlastníka světa
):
    """Smaže konkrétní typ tagu charakteru. Vyžaduje vlastnictví světa."""
    # Ověření vlastníka světa je zajištěno závislostí verify_world_owner
    world = await get_world_or_404(world_id=world_id, db=db)
    db_tag_type = await get_character_tag_type_from_world(tag_type_id=tag_type_id, world=world, db=db)
    
    deleted_tag_type = crud.delete_character_tag_type(db=db, db_tag_type=db_tag_type)
    return deleted_tag_type 