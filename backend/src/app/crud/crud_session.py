from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from .. import models, schemas

def get_session(db: Session, session_id: int) -> Optional[models.Session]:
    """Get a session by its ID, including associated characters."""
    return (
        db.query(models.Session)
        .options(
            joinedload(models.Session.character_associations).joinedload(
                models.SessionCharacter.character
            )
        )
        .filter(models.Session.id == session_id)
        .first()
    )

def get_sessions_by_campaign(
    db: Session, campaign_id: int, skip: int = 0, limit: int = 100
) -> List[models.Session]:
    """Get all sessions belonging to a specific campaign, including associated characters."""
    return (
        db.query(models.Session)
        .options(
            joinedload(models.Session.character_associations).joinedload(
                models.SessionCharacter.character
            )
        )
        .filter(models.Session.campaign_id == campaign_id)
        .order_by(models.Session.date_time.desc().nullslast(), models.Session.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_session(db: Session, session_in: schemas.SessionCreate) -> models.Session:
    """Create a new session. Assumes campaign_id is valid and ownership check happened elsewhere."""
    # TODO: Check if campaign_id exists?
    db_session = models.Session(**session_in.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session(
    db: Session, db_session: models.Session, session_in: schemas.SessionUpdate
) -> models.Session:
    """Update an existing session, including associated characters."""
    update_data = session_in.dict(exclude_unset=True)
    
    # Handle character associations if character_ids is provided
    if "character_ids" in update_data and update_data["character_ids"] is not None:
        character_ids = set(update_data.pop("character_ids")) # Use set for efficient lookup
        
        # Fetch existing character associations for this session
        current_associations = db.query(models.SessionCharacter).filter(
            models.SessionCharacter.session_id == db_session.id
        ).all()
        current_character_ids = {assoc.character_id for assoc in current_associations}

        # Determine which characters to add and which associations to remove
        ids_to_add = character_ids - current_character_ids
        ids_to_remove = current_character_ids - character_ids

        # Remove associations no longer needed
        if ids_to_remove:
            db.query(models.SessionCharacter).filter(
                models.SessionCharacter.session_id == db_session.id,
                models.SessionCharacter.character_id.in_(ids_to_remove)
            ).delete(synchronize_session=False) # Use False for bulk deletes

        # Add new character associations
        for char_id in ids_to_add:
            # Basic check if character exists and belongs to the same world/campaign context if necessary
            # This might require fetching character details or assuming valid IDs are passed
            db.add(models.SessionCharacter(session_id=db_session.id, character_id=char_id))

    # Update other session fields
    for key, value in update_data.items():
        setattr(db_session, key, value)
        
    db.add(db_session) # Add the session itself to the session context if changed
    db.commit()
    db.refresh(db_session)
    
    # Eagerly load characters again after update for the returned object
    db.refresh(db_session, attribute_names=['character_associations'])
    # We might need to explicitly load the nested characters if refresh doesn't handle it
    # This can be complex; ensure the returned object has the updated characters.
    # A simple approach is to re-fetch the session, but refresh is generally preferred.
    
    # Re-query to ensure nested characters are loaded correctly in the returned object
    # This is less efficient but guarantees correctness after modifications
    updated_session_with_chars = get_session(db, db_session.id)
    if updated_session_with_chars:
        return updated_session_with_chars
    else:
         # Fallback or raise error, though it should exist
         db.refresh(db_session)
         return db_session

def delete_session(db: Session, db_session: models.Session) -> models.Session:
    """Delete a session. Assumes ownership check happened elsewhere."""
    # Note: Relationships like SessionCharacter might need handling depending on cascade settings
    # The current model uses cascade="all, delete-orphan" for character_associations
    db.delete(db_session)
    db.commit()
    return db_session 