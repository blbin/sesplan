"""API endpoints for managing Item Tags (associations)."""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....db.session import get_db
from ....auth.auth import get_current_user
from ....core.permissions import check_item_ownership_or_world_membership # Assuming a permission check exists

router = APIRouter()

@router.post("/items/{item_id}/tags/{tag_type_id}", response_model=schemas.ItemTag, status_code=status.HTTP_201_CREATED)
def add_tag_to_item(
    item_id: int,
    tag_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add a specific tag type to an item. User must own the item or be member of the world."""
    # Permission check: Ensure user can modify this item
    # This might involve checking item ownership or world membership/GM status.
    # Using a placeholder function for now.
    db_item = crud.crud_item.get_item(db, item_id=item_id) # Get item to check world_id for permission
    if not db_item:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    check_item_ownership_or_world_membership(db, item_id=item_id, world_id=db_item.world_id, user_id=current_user.id)

    # The CRUD function handles checking tag type validity and existence
    try:
        return crud.crud_item_tag.add_tag_to_item(db=db, item_id=item_id, tag_type_id=tag_type_id)
    except HTTPException as e:
        # Re-raise specific HTTP exceptions from CRUD
        raise e
    except Exception as e:
        # Catch unexpected errors
        print(f"Error adding tag to item: {e}") # Log error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/items/{item_id}/tags/{tag_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag_from_item(
    item_id: int,
    tag_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Remove a specific tag type from an item. User must own the item or be member of the world."""
    # Permission check (similar to add)
    db_item = crud.crud_item.get_item(db, item_id=item_id)
    if not db_item:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    check_item_ownership_or_world_membership(db, item_id=item_id, world_id=db_item.world_id, user_id=current_user.id)

    # The CRUD function handles the logic and 404 if not found
    try:
        deleted_tag = crud.crud_item_tag.remove_tag_from_item(db=db, item_id=item_id, tag_type_id=tag_type_id)
        if deleted_tag:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
             # Should be caught by HTTPException in CRUD, but as a fallback:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag association not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error removing tag from item: {e}") # Log error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# Note: Assumes existence of crud.crud_item.get_item and check_item_ownership_or_world_membership
# We need to import crud_item and permissions if not already available globally in the context
# For now, assume they are accessible via crud.<module_name> 