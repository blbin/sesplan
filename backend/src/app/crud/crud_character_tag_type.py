from sqlalchemy.orm import Session
from .. import models, schemas
from sqlalchemy.exc import IntegrityError

def get_character_tag_type(db: Session, tag_type_id: int) -> models.CharacterTagType | None:
    """Získá konkrétní typ tagu charakteru podle ID."""
    return db.query(models.CharacterTagType).filter(models.CharacterTagType.id == tag_type_id).first()

def get_character_tag_types_by_world(db: Session, world_id: int, skip: int = 0, limit: int = 100) -> list[models.CharacterTagType]:
    """Získá seznam typů tagů charakterů pro daný svět."""
    return db.query(models.CharacterTagType).filter(models.CharacterTagType.world_id == world_id).offset(skip).limit(limit).all()

def create_character_tag_type(db: Session, tag_type_in: schemas.CharacterTagTypeCreate, world_id: int) -> models.CharacterTagType:
    """Vytvoří nový typ tagu charakteru pro daný svět."""
    # Ověření unikátnosti jména v rámci světa (pokud je potřeba)
    # existing = db.query(models.CharacterTagType).filter(models.CharacterTagType.world_id == world_id, models.CharacterTagType.name == tag_type_in.name).first()
    # if existing:
    #     raise ValueError(f"Character tag type with name '{tag_type_in.name}' already exists in this world.")

    db_tag_type = models.CharacterTagType(**tag_type_in.dict(), world_id=world_id)
    db.add(db_tag_type)
    db.commit()
    db.refresh(db_tag_type)
    return db_tag_type

def update_character_tag_type(db: Session, db_tag_type: models.CharacterTagType, tag_type_in: schemas.CharacterTagTypeUpdate) -> models.CharacterTagType:
    """Aktualizuje existující typ tagu charakteru."""
    update_data = tag_type_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tag_type, key, value)
    
    # Ověření unikátnosti jména, pokud se mění
    # if 'name' in update_data:
    #     existing = db.query(models.CharacterTagType).filter(
    #         models.CharacterTagType.world_id == db_tag_type.world_id, 
    #         models.CharacterTagType.name == update_data['name'],
    #         models.CharacterTagType.id != db_tag_type.id
    #     ).first()
    #     if existing:
    #         raise ValueError(f"Character tag type with name '{update_data['name']}' already exists in this world.")
            
    db.add(db_tag_type)
    db.commit()
    db.refresh(db_tag_type)
    return db_tag_type

def delete_character_tag_type(db: Session, db_tag_type: models.CharacterTagType) -> models.CharacterTagType:
    """Smaže typ tagu charakteru."""
    db.delete(db_tag_type)
    db.commit()
    return db_tag_type 