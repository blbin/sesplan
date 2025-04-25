from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.api import dependencies
from app.db.session import get_db
from app.auth.auth import get_current_user

# Tento router bude pravděpodobně vnořen pod /worlds/{world_id}/
router = APIRouter()

@router.post(
    "/", 
    response_model=schemas.OrganizationTagType, 
    status_code=status.HTTP_201_CREATED,
    summary="Vytvořit nový typ tagu pro organizace ve světě"
)
async def create_organization_tag_type(
    *,
    db: Session = Depends(get_db),
    world_id: int = Path(..., description="ID světa, ke kterému typ tagu patří"),
    tag_type_in: schemas.OrganizationTagTypeBase, # Use Base schema, world_id is from path
    current_user: models.User = Depends(get_current_user)
):
    """Vytvoří nový typ tagu pro organizace v rámci konkrétního světa. Vyžaduje vlastnictví světa."""
    # Ověření vlastnictví světa
    await dependencies.verify_world_owner(world_id=world_id, current_user=current_user, db=db)
    
    # Kontrola, zda tag s tímto jménem již ve světě neexistuje (case-insensitive)
    existing_tag = crud.get_organization_tag_type_by_name(db, world_id=world_id, name=tag_type_in.name)
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization tag type with name '{tag_type_in.name}' already exists in this world."
        )

    # Vytvoření tagu s world_id z cesty
    tag_type_create = schemas.OrganizationTagTypeCreate(**tag_type_in.dict(), world_id=world_id)
    new_tag_type = crud.create_organization_tag_type(db=db, tag_type=tag_type_create)
    return new_tag_type

@router.get(
    "/", 
    response_model=List[schemas.OrganizationTagType],
    summary="Získat typy tagů organizací světa"
)
async def read_organization_tag_types(
    *,
    db: Session = Depends(get_db),
    world_id: int = Path(..., description="ID světa, jehož typy tagů chceme získat"),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user) # Ověření členství
):
    """Získá všechny typy tagů pro organizace patřící ke konkrétnímu světu. Vyžaduje členství ve světě."""
    # Ověření členství ve světě
    dependencies.check_world_membership(db=db, world_id=world_id, user_id=current_user.id)
    
    tag_types = crud.get_organization_tag_types_by_world(db, world_id=world_id, skip=skip, limit=limit)
    return tag_types

@router.put(
    "/{tag_type_id}", 
    response_model=schemas.OrganizationTagType,
    summary="Aktualizovat typ tagu organizace"
)
async def update_organization_tag_type(
    *,
    db: Session = Depends(get_db),
    world_id: int = Path(..., description="ID světa"),
    tag_type_id: int = Path(..., description="ID typu tagu k aktualizaci"),
    tag_type_in: schemas.OrganizationTagTypeUpdate,
    current_user: models.User = Depends(get_current_user)
):
    """Aktualizuje existující typ tagu organizace. Vyžaduje vlastnictví světa."""
    # Ověření vlastnictví světa
    await dependencies.verify_world_owner(world_id=world_id, current_user=current_user, db=db)
    
    db_tag_type = crud.get_organization_tag_type(db, tag_type_id=tag_type_id)
    if not db_tag_type or db_tag_type.world_id != world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization tag type not found in this world")

    # Pokud se mění jméno, zkontrolujeme unikátnost nového jména
    if tag_type_in.name and tag_type_in.name.lower() != db_tag_type.name.lower():
        existing_tag = crud.get_organization_tag_type_by_name(db, world_id=world_id, name=tag_type_in.name)
        if existing_tag and existing_tag.id != tag_type_id:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization tag type with name '{tag_type_in.name}' already exists in this world."
            )
            
    updated_tag_type = crud.update_organization_tag_type(db=db, db_tag_type=db_tag_type, tag_type_in=tag_type_in)
    return updated_tag_type

@router.delete(
    "/{tag_type_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Smazat typ tagu organizace"
)
async def delete_organization_tag_type(
    *,
    db: Session = Depends(get_db),
    world_id: int = Path(..., description="ID světa"),
    tag_type_id: int = Path(..., description="ID typu tagu ke smazání"),
    current_user: models.User = Depends(get_current_user)
):
    """Smaže typ tagu organizace. Vyžaduje vlastnictví světa."""
    # Ověření vlastnictví světa
    await dependencies.verify_world_owner(world_id=world_id, current_user=current_user, db=db)
    
    db_tag_type = crud.get_organization_tag_type(db, tag_type_id=tag_type_id)
    if not db_tag_type or db_tag_type.world_id != world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization tag type not found in this world")
        
    crud.delete_organization_tag_type(db=db, db_tag_type=db_tag_type)
    # No content response
    return 