"""API endpoints for managing Item Tag Types."""
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.api import dependencies
from app.api.dependencies import check_world_membership

router = APIRouter()

@router.post("/", response_model=schemas.ItemTagType, status_code=status.HTTP_201_CREATED)
def create_item_tag_type(
    tag_type_in: schemas.ItemTagTypeCreate,
    world_id: int = Path(..., description="ID světa, pro který se typ tagu vytváří"),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Create a new item tag type for a specific world. User must be a member."""
    # Check if user is a member of the world
    check_world_membership(db, world_id, current_user.id)

    # TODO: Check for duplicate tag type name within the world?

    return crud.create_item_tag_type(db=db, tag_type_in=tag_type_in, world_id=world_id)

@router.get("/", response_model=List[schemas.ItemTagType])
def read_item_tag_types(
    world_id: int = Path(..., description="ID světa, ke kterému typy tagů patří"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Retrieve item tag types for a specific world. User must be a member."""
    # Check if user is a member of the world
    check_world_membership(db, world_id, current_user.id)

    tag_types = crud.get_item_tag_types_by_world(db, world_id=world_id, skip=skip, limit=limit)
    return tag_types

@router.put("/{tag_type_id}", response_model=schemas.ItemTagType)
def update_item_tag_type(
    tag_type_in: schemas.ItemTagTypeUpdate,
    tag_type_id: int = Path(..., description="ID typu tagu ke změně"),
    world_id: int = Path(..., description="ID světa"),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Update an item tag type. User must be a member of the world."""
    # Check membership first
    check_world_membership(db, world_id, current_user.id)

    db_tag_type = crud.get_item_tag_type(db, tag_type_id=tag_type_id)
    if not db_tag_type or db_tag_type.world_id != world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item tag type not found in this world")

    # TODO: Check for duplicate name on update?

    return crud.update_item_tag_type(db=db, db_tag_type=db_tag_type, tag_type_in=tag_type_in)

@router.delete("/{tag_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_tag_type(
    tag_type_id: int = Path(..., description="ID typu tagu ke smazání"),
    world_id: int = Path(..., description="ID světa"),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Delete an item tag type. User must be a member of the world."""
    # Check membership first
    check_world_membership(db, world_id, current_user.id)

    db_tag_type = crud.get_item_tag_type(db, tag_type_id=tag_type_id)
    if not db_tag_type or db_tag_type.world_id != world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item tag type not found in this world")

    crud.delete_item_tag_type(db=db, db_tag_type=db_tag_type)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Need to import Response for 204 status code
from fastapi import Response 