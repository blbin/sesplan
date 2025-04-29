from sqlalchemy.orm import Session, joinedload, selectinload
from .. import models # Importujeme models pro použití v options
from ..models import World, WorldUser, Journal # Import Journal model
from ..schemas import CharacterCreate, CharacterUpdate
from .. import schemas 
from typing import List, Optional, Dict, Any

def get_character(db: Session, character_id: int) -> Optional[models.Character]:
    """Get a character by their ID."""
    return db.query(models.Character).filter(models.Character.id == character_id).first()

def get_characters_by_world(db: Session, world_id: int, skip: int = 0, limit: int = 100) -> List[models.Character]:
    """Get characters belonging to a specific world (with pagination), including tags."""
    return (
        db.query(models.Character)
        .options(
            selectinload(models.Character.tags) # Eagerly load tags
            .joinedload(models.CharacterTag.tag_type) # Also load the tag type name
        )
        .filter(models.Character.world_id == world_id)
        .order_by(models.Character.name)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_all_characters_by_world_simple(
    db: Session, world_id: int, skip: int = 0, limit: int = 1000
) -> List[models.Character]:
    """Get all characters belonging to a specific world (for selection lists)."""
    return (
        db.query(models.Character)
        .filter(models.Character.world_id == world_id)
        .order_by(models.Character.name)
        .offset(skip)
        .limit(limit) # Apply limit for safety
        .all()
    )

def get_characters_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Character]:
    """Get all characters owned by a specific user."""
    return (
        db.query(models.Character)
        .filter(models.Character.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_character(db: Session, character_in: CharacterCreate, user_id: int):
    """Create a new character, its associated journal, and assign initial tags.
    The character's user_id will be NULL by default.
    The provided user_id is only used to verify world membership.
    """
    # Check if user (creator) is a member of the world
    world_membership = (
        db.query(WorldUser)
        .filter(
            WorldUser.world_id == character_in.world_id,
            WorldUser.user_id == user_id
        )
        .first()
    )
    if not world_membership:
        return None # Indicate failure: user not in world

    character_data = character_in.dict(exclude_unset=True)
    tag_type_ids = character_data.pop('tag_type_ids', None)

    # Create Character instance WITHOUT assigning the creator's user_id
    # The user_id field in the model should default to None/NULL
    db_character = models.Character(**character_data)
    
    # Create associated Journal instance
    default_journal_name = f"{character_in.name}'s Journal"
    db_journal = Journal(name=default_journal_name, character=db_character)
    
    db.add(db_character)
    db.add(db_journal)

    # Create CharacterTag associations if tag_type_ids were provided
    if tag_type_ids:
        for tag_type_id in tag_type_ids:
            # Optional: Check if tag_type_id actually exists in the world?
            db_tag_association = models.CharacterTag(
                character_id=db_character.id, # Assign after character is added/flushed implicitly? Or set relationship
                character_tag_type_id=tag_type_id
            )
            # Better approach: Use relationship append if character object is known
            # db_tag_association = models.CharacterTag(character_tag_type_id=tag_type_id)
            # db_character.tags.append(db_tag_association)
            # For simplicity now, let's add directly, assuming ID is known after add/flush
            # Revisit if character_id is null here.
            # It seems safer to use the relationship:            
            db_tag = models.CharacterTag(character_tag_type_id=tag_type_id)
            db_character.tags.append(db_tag) # Append to relationship
            # db.add(db_tag) # SQLAlchemy handles adding via cascade with relationship append
    
    try:
        db.commit()
    except Exception as e:
        db.rollback() 
        raise e

    db.refresh(db_character)
    db.refresh(db_journal)
    
    return db_character

def update_character(
    db: Session, db_character: models.Character, character_in: CharacterUpdate
) -> models.Character:
    """Update an existing character. Handles tag updates and journal renaming."""
    update_data = character_in.dict(exclude_unset=True)
    
    # --- Update Journal Name if Character Name changes --- 
    if 'name' in update_data and db_character.journal:
        new_character_name = update_data['name']
        db_character.journal.name = f"{new_character_name}'s Journal"
        # No need to db.add(db_character.journal) separately, SQLAlchemy tracks changes
        # on related objects loaded within the session.

    tag_type_ids = update_data.pop('tag_type_ids', None) # Extract tag IDs

    # Update standard fields
    for key, value in update_data.items():
        setattr(db_character, key, value)
    
    # Handle tag updates if provided
    if tag_type_ids is not None:
        # Get current tag type IDs for the character
        current_tag_ids = {tag.character_tag_type_id for tag in db_character.tags}
        new_tag_ids = set(tag_type_ids)

        # Tags to add
        ids_to_add = new_tag_ids - current_tag_ids
        for tag_type_id in ids_to_add:
            db_tag = models.CharacterTag(character_tag_type_id=tag_type_id)
            db_character.tags.append(db_tag)
        
        # Tags to remove
        ids_to_remove = current_tag_ids - new_tag_ids
        if ids_to_remove:
             # Filter and delete existing tag associations
             # Iterate over a copy of the list when removing items
             for tag_association in list(db_character.tags):
                 if tag_association.character_tag_type_id in ids_to_remove:
                     db.delete(tag_association) # Mark for deletion
                     # Or db_character.tags.remove(tag_association) if cascade works correctly

    db.add(db_character) # Add the character itself (updates and new tags)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
        
    db.refresh(db_character)
    return db_character

def delete_character(db: Session, db_character: models.Character) -> models.Character:
    """Delete a character. Journal and tags should be deleted via cascade."""
    db.delete(db_character)
    db.commit()
    return db_character # Return the deleted object (optional)

def get_all_characters_in_world(db: Session, world_id: int) -> List[models.Character]:
    """Fetches all characters belonging to a specific world without pagination."""
    return db.query(models.Character).filter(models.Character.world_id == world_id).all()

def assign_user_to_character(db: Session, db_character: models.Character, user_id: Optional[int]) -> models.Character:
    """Assigns or unassigns a user to a character."""
    db_character.user_id = user_id
    db.add(db_character)
    try:
        db.commit()
        db.refresh(db_character)
    except Exception as e:
        db.rollback()
        raise e
    return db_character 

def create_character_for_user(db: Session, character_in: schemas.CharacterCreate, owner_user_id: int) -> Optional[models.Character]:
    """Creates a new character and assigns it to a specific user, bypassing world membership check.
       Also creates the associated journal.
    """
    # Basic check if world exists (optional but good practice)
    world_exists = db.query(World).filter(World.id == character_in.world_id).first()
    if not world_exists:
        print(f"Attempted to create character in non-existent world: {character_in.world_id}")
        return None
    
    # Basic check if user exists (optional but good practice)
    owner_exists = db.query(models.User).filter(models.User.id == owner_user_id).first()
    if not owner_exists:
        print(f"Attempted to assign character to non-existent user: {owner_user_id}")
        return None

    character_data = character_in.model_dump(exclude_unset=True) # Use model_dump for Pydantic v2
    # Remove fields that might be in schema but not in model directly for creation
    tag_type_ids = character_data.pop('tag_type_ids', None) # Handle potential tags if needed, though unlikely for this context

    # Create Character instance and directly assign owner_user_id
    db_character = models.Character(
        **character_data, 
        user_id=owner_user_id # Assign the owner directly
    )
    
    # Create associated Journal instance
    default_journal_name = f"{character_in.name}'s Journal"
    db_journal = Journal(name=default_journal_name, character=db_character)
    
    db.add(db_character)
    db.add(db_journal)

    # Handle potential tags if necessary (unlikely for invite context)
    if tag_type_ids:
        for tag_type_id in tag_type_ids:
            db_tag = models.CharacterTag(character_tag_type_id=tag_type_id)
            db_character.tags.append(db_tag)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error creating character for user {owner_user_id}: {e}")
        # Consider logging the error properly
        return None # Return None on commit error

    db.refresh(db_character)
    db.refresh(db_journal) # Refresh journal as well
    
    return db_character 