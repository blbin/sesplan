"""CRUD operations for ItemTag associations."""
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from fastapi import HTTPException, status

from .. import models, schemas

def add_tag_to_item(db: Session, item_id: int, tag_type_id: int) -> models.ItemTag:
    """Add a tag (by type ID) to an item. Ensures tag type exists and association doesn't already exist."""
    # Check if item exists (optional, could be handled by FK constraint or endpoint logic)
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    # Check if tag type exists and belongs to the same world as the item
    db_tag_type = db.query(models.ItemTagType).filter(
        models.ItemTagType.id == tag_type_id,
        models.ItemTagType.world_id == db_item.world_id # Ensure tag type is valid for the item's world
    ).first()
    if not db_tag_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item tag type not found or not valid for this world")

    # Check if the tag association already exists
    already_exists = db.query(exists().where(
        models.ItemTag.item_id == item_id,
        models.ItemTag.item_tag_type_id == tag_type_id
    )).scalar()

    if already_exists:
        # Optionally, return the existing tag or raise a specific error/warning
        # For now, let's raise an error to prevent duplicates
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already assigned to this item")

    # Create the new tag association
    db_item_tag = models.ItemTag(item_id=item_id, item_tag_type_id=tag_type_id)
    db.add(db_item_tag)
    db.commit()
    db.refresh(db_item_tag)
    return db_item_tag

def remove_tag_from_item(db: Session, item_id: int, tag_type_id: int) -> models.ItemTag | None:
    """Remove a tag (by type ID) from an item."""
    db_item_tag = db.query(models.ItemTag).filter(
        models.ItemTag.item_id == item_id,
        models.ItemTag.item_tag_type_id == tag_type_id
    ).first()

    if db_item_tag:
        db.delete(db_item_tag)
        db.commit()
        # Return the deleted object (or its ID) for confirmation
        return db_item_tag
    else:
        # Tag association not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag association not found for this item")

# Note: We might need a function to get tags for an item, but often the relationship
# loading on the Item model itself is sufficient (e.g., in the get_item CRUD function). 