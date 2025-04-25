from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from .. import models, schemas

def get_character_tag(db: Session, character_id: int, tag_type_id: int) -> models.CharacterTag | None:
    """Získá přiřazení tagu k charakteru podle ID charakteru a ID typu tagu."""
    return db.query(models.CharacterTag).filter(
        models.CharacterTag.character_id == character_id, 
        models.CharacterTag.character_tag_type_id == tag_type_id
    ).first()

def add_tag_to_character(db: Session, character_id: int, tag_type_id: int) -> models.CharacterTag:
    """Přidá tag k charakteru. Ověří, zda tag type existuje a patří ke světu charakteru."""
    
    # Získání charakteru pro ověření světa
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if not db_character:
        # Tato chyba by neměla nastat, pokud se používá závislost get_character_or_404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    # Získání typu tagu a ověření, že patří ke stejnému světu
    db_tag_type = db.query(models.CharacterTagType).filter(models.CharacterTagType.id == tag_type_id).first()
    if not db_tag_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character tag type not found")
    if db_tag_type.world_id != db_character.world_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag type does not belong to the character's world")

    # Ověření, zda tag již není přiřazen
    db_existing_tag = get_character_tag(db, character_id=character_id, tag_type_id=tag_type_id)
    if db_existing_tag:
        # Tag již existuje, můžeme ho vrátit nebo vyvolat chybu/nic nedělat
        return db_existing_tag 

    # Vytvoření nového přiřazení
    db_tag = models.CharacterTag(character_id=character_id, character_tag_type_id=tag_type_id)
    db.add(db_tag)
    try:
        db.commit()
        db.refresh(db_tag)
    except IntegrityError:
        db.rollback()
        # Může nastat race condition, znovu zkusíme získat tag
        db_existing_tag = get_character_tag(db, character_id=character_id, tag_type_id=tag_type_id)
        if db_existing_tag:
             return db_existing_tag
        else:
            # Pokud ani teď neexistuje, je problém jinde
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not assign tag")
             
    return db_tag

def remove_tag_from_character(db: Session, character_id: int, tag_type_id: int) -> models.CharacterTag | None:
    """Odebere tag z charakteru."""
    db_tag = get_character_tag(db, character_id=character_id, tag_type_id=tag_type_id)
    if db_tag:
        db.delete(db_tag)
        db.commit()
        return db_tag
    return None # Tag nebyl nalezen 