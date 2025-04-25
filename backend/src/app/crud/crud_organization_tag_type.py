from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.organization_tag_type import OrganizationTagType
from ..schemas.organization_tag_type import OrganizationTagTypeCreate, OrganizationTagTypeUpdate

def get_organization_tag_type(db: Session, tag_type_id: int):
    """Gets a specific organization tag type by its ID."""
    return db.query(OrganizationTagType).filter(OrganizationTagType.id == tag_type_id).first()

def get_organization_tag_type_by_name(db: Session, world_id: int, name: str):
    """Gets a specific organization tag type by its name within a world."""
    return db.query(OrganizationTagType).filter(
        OrganizationTagType.world_id == world_id,
        func.lower(OrganizationTagType.name) == func.lower(name)
    ).first()

def get_organization_tag_types_by_world(db: Session, world_id: int, skip: int = 0, limit: int = 100):
    """Gets all organization tag types belonging to a specific world."""
    return (
        db.query(OrganizationTagType)
        .filter(OrganizationTagType.world_id == world_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_organization_tag_type(db: Session, tag_type: OrganizationTagTypeCreate):
    """Creates a new organization tag type."""
    db_tag_type = OrganizationTagType(**tag_type.dict())
    db.add(db_tag_type)
    db.commit()
    db.refresh(db_tag_type)
    return db_tag_type

def update_organization_tag_type(db: Session, db_tag_type: OrganizationTagType, tag_type_in: OrganizationTagTypeUpdate):
    """Updates an organization tag type."""
    update_data = tag_type_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tag_type, key, value)
    db.add(db_tag_type)
    db.commit()
    db.refresh(db_tag_type)
    return db_tag_type

def delete_organization_tag_type(db: Session, db_tag_type: OrganizationTagType):
    """Deletes an organization tag type."""
    db.delete(db_tag_type)
    db.commit()
    # No need to return the deleted object usually for tag types
    return db_tag_type # Return instance for now, consistent with others 