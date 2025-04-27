from sqlalchemy.orm import Session, joinedload, outerjoin
from sqlalchemy import select, label
from typing import List, Optional
from ..models.item import Item
from ..models.character import Character
from ..models.item_tag import ItemTag
from ..schemas.item import ItemCreate, ItemUpdate, Item as ItemSchema

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
    stmt = (
        select(
            Item, 
            label('assigned_character_name', Character.name)
        )
        .outerjoin(Character, Item.character_id == Character.id)
        .filter(Item.world_id == world_id)
        .options(joinedload(Item.tags).joinedload(ItemTag.tag_type))
    )

    if character_id is not None:
        stmt = stmt.filter(Item.character_id == character_id)
    if location_id is not None:
        stmt = stmt.filter(Item.location_id == location_id)
    
    stmt = stmt.order_by(Item.id)
    
    stmt = stmt.offset(skip).limit(limit)
    
    results = db.execute(stmt).unique().all()

    items_with_names = []
    for item_obj, char_name in results:
        item_dto = ItemSchema.from_orm(item_obj)
        item_dto.assigned_character_name = char_name
        items_with_names.append(item_dto)

    return items_with_names

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