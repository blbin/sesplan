from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.item import Item
from ..schemas.item import ItemCreate, ItemUpdate

def get_item(db: Session, item_id: int) -> Optional[Item]:
    """Získá konkrétní item podle jeho ID."""
    return db.query(Item).filter(Item.id == item_id).first()

def get_items_by_world(
    db: Session,
    world_id: int,
    character_id: Optional[int] = None,
    location_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Item]:
    """Získá seznam itemů patřících ke světu, volitelně filtrovaných podle postavy nebo lokace."""
    query = db.query(Item).filter(Item.world_id == world_id)
    if character_id is not None:
        query = query.filter(Item.character_id == character_id)
    if location_id is not None:
        query = query.filter(Item.location_id == location_id)
    return query.offset(skip).limit(limit).all()

def create_item(db: Session, item: ItemCreate) -> Item:
    """Vytvoří nový item v databázi."""
    # Zde můžeme přidat validaci, zda character_id a location_id patří ke stejnému world_id
    # Ale to by mělo být spíše v API vrstvě nebo service vrstvě
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, db_item: Item, item_in: ItemUpdate) -> Item:
    """Aktualizuje existující item."""
    update_data = item_in.dict(exclude_unset=True)
    
    # Zpracování explicitního nastavení na null pro character_id a location_id
    if "character_id" in item_in.dict(exclude_none=False) and item_in.character_id is None:
         update_data["character_id"] = None
    if "location_id" in item_in.dict(exclude_none=False) and item_in.location_id is None:
         update_data["location_id"] = None
    
    for key, value in update_data.items():
        setattr(db_item, key, value)
        
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, db_item: Item) -> Item:
    """Smaže item z databáze."""
    db.delete(db_item)
    db.commit()
    return db_item 