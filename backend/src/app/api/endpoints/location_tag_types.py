from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
# Importujeme sdílené závislosti
from ..dependencies import get_world_or_404, verify_world_owner, check_world_membership

router = APIRouter()

# Závislost pro získání tag type a ověření příslušnosti ke světu
async def get_tag_type_from_world(
    tag_type_id: int = Path(..., description="ID typu tagu lokace"),
    world: models.World = Depends(get_world_or_404),
    db: Session = Depends(get_db)
) -> models.LocationTagType:
    db_tag_type = crud.get_location_tag_type(db, tag_type_id=tag_type_id)
    if not db_tag_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location tag type not found")
    if db_tag_type.world_id != world.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Location tag type does not belong to this world"
        )
    return db_tag_type

@router.post(
    "", 
    response_model=schemas.LocationTagType, 
    status_code=status.HTTP_201_CREATED, 
    summary="Vytvořit nový typ tagu pro lokace ve světě"
)
async def create_location_tag_type(
    *,
    world_id: int,
    tag_type_in: schemas.LocationTagTypeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    # Ověření vlastníka světa pomocí závislosti
    # verify_world_owner bere world_id a current_user
    # Poznámka: Ověření vlastníka se teď spoléhá na explicitní volání níže,
    # protože předání world_id z prefixu do závislosti závislosti je komplikované.
    # _=Depends(lambda world_id=Path(...): verify_world_owner(world_id=world_id, current_user=Depends(get_current_user), db=Depends(get_db)))
):
    """Vytvoří nový typ tagu pro lokace v rámci specifikovaného světa. Vyžaduje vlastnictví světa."""
    # Ověření vlastníka světa (explicitně)
    # world_id je nyní běžný parametr funkce
    await verify_world_owner(world_id=world_id, current_user=current_user, db=db)
    # Ověření existence světa je implicitně součástí verify_world_owner
    
    try:
        db_tag_type = crud.create_location_tag_type(db=db, tag_type_in=tag_type_in, world_id=world_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return db_tag_type

@router.get("", response_model=List[schemas.LocationTagType], summary="Získat typy tagů lokací světa")
def read_location_tag_types(
    *, 
    world_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """Získá seznam všech typů tagů pro lokace v rámci specifikovaného světa. Vyžaduje členství ve světě."""
    # Ověříme členství uživatele ve světě
    check_world_membership(db, world_id, current_user.id)
    
    # Poznámka: Existence světa je implicitně ověřena, pokud check_world_membership nevrátí 403
    # (protože world_user záznam bez existujícího světa by neměl existovat díky FK constraints)
    
    tag_types = crud.get_location_tag_types_by_world(db=db, world_id=world_id, skip=skip, limit=limit)
    return tag_types

@router.put("/{tag_type_id}", response_model=schemas.LocationTagType, summary="Aktualizovat typ tagu lokace")
async def update_location_tag_type(
    *,
    world_id: int,
    tag_type_id: int = Path(..., description="ID typu tagu lokace"), # tag_type_id je v cestě tohoto endpointu
    tag_type_in: schemas.LocationTagTypeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    # Ověření vlastníka
    # _=Depends(lambda world_id=Path(...): verify_world_owner(world_id=world_id, current_user=Depends(get_current_user), db=Depends(get_db)))
):
    """Aktualizuje konkrétní typ tagu lokace. Vyžaduje vlastnictví světa."""
    # Ověření vlastníka světa (explicitně)
    # world_id je nyní běžný parametr funkce
    await verify_world_owner(world_id=world_id, current_user=current_user, db=db)
    
    # Získáme tag type a ověříme, že patří ke světu
    # Předáme world_id přímo do get_world_or_404
    db_tag_type = await get_tag_type_from_world(tag_type_id=tag_type_id, world=await get_world_or_404(world_id=world_id, db=db), db=db)

    try:
        updated_tag_type = crud.update_location_tag_type(db=db, db_tag_type=db_tag_type, tag_type_in=tag_type_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return updated_tag_type

@router.delete("/{tag_type_id}", response_model=schemas.LocationTagType, summary="Smazat typ tagu lokace")
async def delete_location_tag_type(
    *,
    world_id: int,
    tag_type_id: int = Path(..., description="ID typu tagu lokace"), # tag_type_id je v cestě tohoto endpointu
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    # Ověření vlastníka
    # _=Depends(lambda world_id=Path(...): verify_world_owner(world_id=world_id, current_user=Depends(get_current_user), db=Depends(get_db)))
):
    """Smaže konkrétní typ tagu lokace. Vyžaduje vlastnictví světa."""
    # Ověření vlastníka světa (explicitně)
    # world_id je nyní běžný parametr funkce
    await verify_world_owner(world_id=world_id, current_user=current_user, db=db)

    # Získáme tag type a ověříme, že patří ke světu
    # Předáme world_id přímo do get_world_or_404
    db_tag_type = await get_tag_type_from_world(tag_type_id=tag_type_id, world=await get_world_or_404(world_id=world_id, db=db), db=db)
    
    deleted_tag_type = crud.delete_location_tag_type(db=db, db_tag_type=db_tag_type)
    return deleted_tag_type 