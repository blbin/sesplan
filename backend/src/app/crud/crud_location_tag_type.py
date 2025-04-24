from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas

def get_location_tag_type(db: Session, tag_type_id: int) -> Optional[models.LocationTagType]:
    """Získá typ tagu lokace podle ID."""
    return db.query(models.LocationTagType).filter(models.LocationTagType.id == tag_type_id).first()

def get_location_tag_types_by_world(
    db: Session, world_id: int, skip: int = 0, limit: int = 100
) -> List[models.LocationTagType]:
    """Získá všechny typy tagů lokací pro daný svět."""
    return (
        db.query(models.LocationTagType)
        .filter(models.LocationTagType.world_id == world_id)
        .order_by(models.LocationTagType.name)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_location_tag_type(
    db: Session, tag_type_in: schemas.LocationTagTypeCreate, world_id: int
) -> models.LocationTagType:
    """Vytvoří nový typ tagu lokace."""
    # Ověření, zda už neexistuje tag se stejným jménem v daném světě?
    existing_tag = db.query(models.LocationTagType).filter(
        models.LocationTagType.world_id == world_id,
        models.LocationTagType.name == tag_type_in.name
    ).first()
    if existing_tag:
        # Možná bychom měli vrátit chybu nebo existující tag?
        # Prozatím vrátíme chybu (nebo necháme DB vyhodit unique constraint error, pokud je nastaven)
        # V API vrstvě bychom měli hodit HTTPException
        raise ValueError(f"Location tag type with name '{tag_type_in.name}' already exists in this world.")
        
    db_tag_type = models.LocationTagType(**tag_type_in.dict(), world_id=world_id)
    db.add(db_tag_type)
    db.commit()
    db.refresh(db_tag_type)
    return db_tag_type

def update_location_tag_type(
    db: Session, db_tag_type: models.LocationTagType, tag_type_in: schemas.LocationTagTypeUpdate
) -> models.LocationTagType:
    """Aktualizuje existující typ tagu lokace."""
    update_data = tag_type_in.dict(exclude_unset=True)
    
    # Pokud se mění jméno, ověříme unikátnost v rámci světa
    if "name" in update_data and update_data["name"] != db_tag_type.name:
        existing_tag = db.query(models.LocationTagType).filter(
            models.LocationTagType.world_id == db_tag_type.world_id,
            models.LocationTagType.name == update_data["name"],
            models.LocationTagType.id != db_tag_type.id # Vyloučíme sebe sama
        ).first()
        if existing_tag:
            raise ValueError(f"Location tag type with name '{update_data['name']}' already exists in this world.")
            
    for key, value in update_data.items():
        setattr(db_tag_type, key, value)
    db.add(db_tag_type)
    db.commit()
    db.refresh(db_tag_type)
    return db_tag_type

def delete_location_tag_type(db: Session, db_tag_type: models.LocationTagType) -> models.LocationTagType:
    """Smaže typ tagu lokace. Cascade by měl smazat i LocationTag záznamy."""
    db.delete(db_tag_type)
    db.commit()
    return db_tag_type 