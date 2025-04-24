from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from .. import models

def get_location_tag_association(
    db: Session, location_id: int, tag_type_id: int
) -> Optional[models.LocationTag]:
    """Získá záznam o přiřazení tagu k lokaci, pokud existuje."""
    return (
        db.query(models.LocationTag)
        .filter(
            models.LocationTag.location_id == location_id,
            models.LocationTag.location_tag_type_id == tag_type_id
        )
        .first()
    )

def add_tag_to_location(
    db: Session, location_id: int, tag_type_id: int
) -> models.LocationTag:
    """Přiřadí typ tagu k lokaci. Ověří, že tag i lokace existují a patří ke stejnému světu."""
    # 1. Získáme lokaci
    db_location = db.query(models.Location).filter(models.Location.id == location_id).first()
    if not db_location:
        raise ValueError("Location not found")

    # 2. Získáme typ tagu
    db_tag_type = db.query(models.LocationTagType).filter(models.LocationTagType.id == tag_type_id).first()
    if not db_tag_type:
        raise ValueError("Location tag type not found")

    # 3. Ověříme, že patří ke stejnému světu
    if db_location.world_id != db_tag_type.world_id:
        raise ValueError("Location and Tag Type do not belong to the same world")

    # 4. Ověříme, zda už přiřazení neexistuje
    existing_association = get_location_tag_association(db, location_id=location_id, tag_type_id=tag_type_id)
    if existing_association:
        return existing_association # Pokud už existuje, vrátíme ho

    # 5. Vytvoříme nové přiřazení
    db_association = models.LocationTag(location_id=location_id, location_tag_type_id=tag_type_id)
    db.add(db_association)
    db.commit()
    db.refresh(db_association)
    return db_association

def remove_tag_from_location(db: Session, location_id: int, tag_type_id: int) -> bool:
    """Odebere přiřazení typu tagu od lokace. Vrací True, pokud bylo něco smazáno."""
    db_association = get_location_tag_association(db, location_id=location_id, tag_type_id=tag_type_id)
    if db_association:
        db.delete(db_association)
        db.commit()
        return True
    return False

def get_tags_for_location(db: Session, location_id: int) -> List[models.LocationTag]:
    """Získá všechny tagy (LocationTag záznamy) přiřazené k lokaci."""
    # Použijeme joinedload pro efektivní načtení tag_type
    return (
        db.query(models.LocationTag)
        .options(joinedload(models.LocationTag.tag_type))
        .filter(models.LocationTag.location_id == location_id)
        .all()
    ) 