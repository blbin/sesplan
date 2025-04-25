"""CRUD operations for ItemTagType model."""
from sqlalchemy.orm import Session
from .. import models, schemas

def get_item_tag_type(db: Session, tag_type_id: int, world_id: int) -> models.ItemTagType | None:
    """Get a specific item tag type by ID within a world."""
    return db.query(models.ItemTagType).filter(
        models.ItemTagType.id == tag_type_id,
        models.ItemTagType.world_id == world_id
    ).first()

def get_item_tag_types_by_world(db: Session, world_id: int, skip: int = 0, limit: int = 100) -> list[models.ItemTagType]:
    """Get all item tag types for a specific world."""
    return db.query(models.ItemTagType).filter(models.ItemTagType.world_id == world_id).offset(skip).limit(limit).all()

def create_item_tag_type(db: Session, tag_type_in: schemas.ItemTagTypeCreate, world_id: int) -> models.ItemTagType:
    """Create a new item tag type for a world."""
    db_tag_type = models.ItemTagType(
        **tag_type_in.model_dump(),
        world_id=world_id
    )
    db.add(db_tag_type)
    db.commit()
    db.refresh(db_tag_type)
    return db_tag_type

def update_item_tag_type(db: Session, db_tag_type: models.ItemTagType, tag_type_in: schemas.ItemTagTypeUpdate) -> models.ItemTagType:
    """Update an existing item tag type."""
    update_data = tag_type_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tag_type, key, value)
    db.add(db_tag_type)
    db.commit()
    db.refresh(db_tag_type)
    return db_tag_type

def delete_item_tag_type(db: Session, db_tag_type: models.ItemTagType) -> models.ItemTagType:
    """Delete an item tag type."""
    db.delete(db_tag_type)
    db.commit()
    # Note: After deletion, the object might not be fully usable depending on session state.
    # Returning it might be problematic. Consider returning ID or None/True.
    # For consistency with other delete operations, we return the object for now.
    return db_tag_type 