from sqlalchemy.orm import Session, joinedload
from ..models.organization import Organization
from ..models.organization_tag import OrganizationTag
from ..models.organization_tag_type import OrganizationTagType

def get_organization_tag_association(db: Session, organization_id: int, tag_type_id: int):
    """Gets a specific tag association for an organization."""
    return (
        db.query(OrganizationTag)
        .filter(
            OrganizationTag.organization_id == organization_id,
            OrganizationTag.organization_tag_type_id == tag_type_id
        )
        .first()
    )

def get_tags_for_organization(db: Session, organization_id: int):
    """Gets all tags associated with a specific organization, loading the tag type details."""
    return (
        db.query(OrganizationTag)
        .options(joinedload(OrganizationTag.tag_type))
        .filter(OrganizationTag.organization_id == organization_id)
        .all()
    )

def add_tag_to_organization(db: Session, organization_id: int, tag_type_id: int) -> OrganizationTag:
    """Adds a tag type to an organization. Raises ValueError on issues."""
    # 1. Check if organization exists
    db_organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not db_organization:
        raise ValueError("Organization not found")

    # 2. Check if tag type exists and belongs to the same world
    db_tag_type = db.query(OrganizationTagType).filter(OrganizationTagType.id == tag_type_id).first()
    if not db_tag_type:
        raise ValueError("Tag type not found")
    if db_tag_type.world_id != db_organization.world_id:
        raise ValueError("Tag type belongs to a different world")

    # 3. Check if association already exists
    db_existing_association = get_organization_tag_association(db, organization_id, tag_type_id)
    if db_existing_association:
        return db_existing_association # Or raise an error/return None if preferred

    # 4. Create new association
    db_association = OrganizationTag(
        organization_id=organization_id,
        organization_tag_type_id=tag_type_id
    )
    db.add(db_association)
    db.commit()
    db.refresh(db_association)
    # Eager load the tag_type for the response
    db.refresh(db_association, attribute_names=["tag_type"])
    return db_association

def remove_tag_from_organization(db: Session, organization_id: int, tag_type_id: int) -> bool:
    """Removes a tag association from an organization. Returns True if deleted, False otherwise."""
    db_association = get_organization_tag_association(db, organization_id, tag_type_id)
    if db_association:
        db.delete(db_association)
        db.commit()
        return True
    return False 