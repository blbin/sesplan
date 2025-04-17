from sqlalchemy.orm import Session
from ..models import Character, World, WorldUser # Přidán WorldUser
from ..schemas import CharacterCreate, CharacterUpdate

def get_character(db: Session, character_id: int):
    return db.query(Character).filter(Character.id == character_id).first()

def get_characters_by_world(db: Session, world_id: int, user_id: int, skip: int = 0, limit: int = 100):
    """Get characters for a specific world owned by the user."""
    return db.query(Character).filter(Character.world_id == world_id, Character.user_id == user_id).offset(skip).limit(limit).all()

def get_all_characters_in_world(db: Session, world_id: int, skip: int = 0, limit: int = 100):
    """Gets all characters belonging to a specific world."""
    return db.query(Character).filter(Character.world_id == world_id).offset(skip).limit(limit).all()

def get_characters_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all characters owned by the user across all worlds."""
    return db.query(Character).filter(Character.user_id == user_id).offset(skip).limit(limit).all()

def create_character(db: Session, character_in: CharacterCreate, user_id: int):
    """Create a new character. User must be a member of the world."""
    # Check if user is a member of the world
    world_membership = (
        db.query(WorldUser)
        .filter(
            WorldUser.world_id == character_in.world_id,
            WorldUser.user_id == user_id
        )
        .first()
    )
    if not world_membership:
        # User is not a member of the world or world doesn't exist
        return None # Indicate failure

    # Vytvoření postavy
    db_character = Character(**character_in.dict(), user_id=user_id)
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

def update_character(db: Session, db_character: Character, character_in: CharacterUpdate):
    """Update a character. Assumes ownership check happened in the API layer."""
    update_data = character_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_character, key, value)
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

def delete_character(db: Session, db_character: Character):
    """Delete a character. Assumes ownership check happened in the API layer."""
    db.delete(db_character)
    db.commit()
    return db_character 