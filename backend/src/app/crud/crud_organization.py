from sqlalchemy.orm import Session, joinedload
from ..models.organization import Organization
from ..models.organization_tag import OrganizationTag
from ..schemas.organization import OrganizationCreate, OrganizationUpdate


def get_organization(db: Session, organization_id: int):
    """Gets a specific organization by its ID, including its tags and tag types."""
    return (
        db.query(Organization)
        .options(joinedload(Organization.tags).joinedload(OrganizationTag.tag_type))
        .filter(Organization.id == organization_id)
        .first()
    )


def get_organizations_by_world(db: Session, world_id: int, skip: int = 0, limit: int = 100):
    """Gets all organizations belonging to a specific world."""
    return (
        db.query(Organization)
        .filter(Organization.world_id == world_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_organization(db: Session, organization: OrganizationCreate):
    """Creates a new organization."""
    db_organization = Organization(**organization.dict())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def update_organization(db: Session, db_organization: Organization, organization_in: OrganizationUpdate):
    """Updates an organization. Assumes authorization check happened in the API layer."""
    update_data = organization_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_organization, key, value)
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def delete_organization(db: Session, db_organization: Organization):
    """Deletes an organization. Assumes authorization check happened in the API layer."""
    db.delete(db_organization)
    db.commit()
    # Return the deleted object data before the session is closed/invalidated
    # If relationships were loaded, they might become invalid after commit,
    # depending on cascade settings and session state.
    # Consider returning just an ID or a basic confirmation if needed.
    return db_organization # Returning the instance for now 