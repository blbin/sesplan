"""API endpoints for managing Item Tags (associations)."""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Path
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.api import dependencies
from app.auth.auth import get_current_user
from app.api.dependencies import check_world_membership

router = APIRouter()

@router.post("/{tag_type_id}", response_model=schemas.ItemTag, status_code=status.HTTP_201_CREATED)
def add_tag_to_item(
    item_id: int = Path(..., description="ID of the item to add tag to"), 
    tag_type_id: int = Path(..., description="ID of the tag type to assign"), 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Assigns an item tag type to an item. User must be member of the world."""
    # 1. Get the item to find its world_id
    db_item = crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    # 2. Check if user is member of the world the item belongs to
    check_world_membership(db, world_id=db_item.world_id, user_id=current_user.id)
    
    # 3. Check if the tag type exists and belongs to the same world (Done inside crud.add_tag_to_item)
    # db_tag_type = crud.get_item_tag_type(db, tag_type_id=tag_type_id, world_id=db_item.world_id)
    # if not db_tag_type:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item tag type not found in this world")

    # 4. Check if tag is already assigned (Done inside crud.add_tag_to_item)
    # existing_tag = crud.get_item_tag_by_item_and_type(db, item_id=item_id, tag_type_id=tag_type_id)
    # if existing_tag:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already assigned to this item")

    # 5. Create the tag assignment (Handles checks internally)
    try:
        return crud.add_tag_to_item(db=db, item_id=item_id, tag_type_id=tag_type_id)
    except HTTPException as e:
        # Re-raise HTTPExceptions raised by the CRUD function (like 409 conflict or 404 for tag type)
        raise e
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error adding tag to item: {e}") # Log error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add tag to item")

@router.delete("/{tag_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag_from_item(
    item_id: int = Path(..., description="ID of the item to remove tag from"), 
    tag_type_id: int = Path(..., description="ID of the tag type to remove"), 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Removes an item tag type from an item. User must be member of the world."""
    # 1. Get the item to find its world_id
    db_item = crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    # 2. Check if user is member of the world the item belongs to
    check_world_membership(db, world_id=db_item.world_id, user_id=current_user.id)

    # 3. Delete the tag assignment (Handles checks internally)
    try:
        deleted_tag = crud.remove_tag_from_item(db=db, item_id=item_id, tag_type_id=tag_type_id)
        # crud.remove_tag_from_item raises 404 if not found, so no need to check result here
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException as e:
         # Re-raise HTTPExceptions raised by the CRUD function (like 404)
        raise e
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error removing tag from item: {e}") # Log error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove tag from item")

# Note: Assumes existence of crud.crud_item.get_item and check_item_ownership_or_world_membership
# We need to import crud_item and permissions if not already available globally in the context
# For now, assume they are accessible via crud.<module_name> 