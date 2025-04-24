from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, models, schemas
from app.api import dependencies # Správný import závislostí
from app.db.session import get_db
from app.auth.auth import get_current_user
# Explicitní import pro ověření vlastnictví světa
# from .locations import verify_world_owner # Chybný import
from ..dependencies import verify_world_owner # Správný import ze sdílených závislostí

router = APIRouter()

# --- Helper Functions / Dependencies (pro validaci) ---

def get_item_or_404(db: Session, item_id: int) -> models.Item:
    """Pomocná funkce pro získání itemu nebo vyvolání 404."""
    db_item = crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return db_item

async def validate_item_relations(
    db: Session,
    world_id: int,
    character_id: Optional[int] = None,
    location_id: Optional[int] = None
):
    """Validuje, zda character_id a location_id existují a patří do daného světa."""
    if character_id:
        character = crud.get_character(db, character_id=character_id)
        if not character or character.world_id != world_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid character_id {character_id} for world {world_id}")
    if location_id:
        location = crud.get_location(db, location_id=location_id)
        if not location or location.world_id != world_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid location_id {location_id} for world {world_id}")

# Nová závislost pro ověření vlastníka světa na základě ItemCreate
async def verify_item_world_owner(
    item_in: schemas.ItemCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ověří, zda aktuální uživatel vlastní svět specifikovaný v ItemCreate."""
    await verify_world_owner(world_id=item_in.world_id, current_user=current_user, db=db)
    # Není potřeba nic vracet, jde jen o ověření

# --- API Endpoints ---

@router.post("/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    *,
    db: Session = Depends(get_db),
    item_in: schemas.ItemCreate,
    # Použijeme novou, čistší závislost
    _: None = Depends(verify_item_world_owner)
):
    """Vytvoří nový item ve světě. Vyžaduje vlastnictví světa."""
    # Validace existence a příslušnosti character_id a location_id ke světu
    await validate_item_relations(
        db=db,
        world_id=item_in.world_id,
        character_id=item_in.character_id,
        location_id=item_in.location_id
    )
    
    item = crud.create_item(db=db, item=item_in)
    return item

@router.get("/{item_id}", response_model=schemas.Item)
def read_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    # current_user: models.User = Depends(get_current_user) # Zatím není potřeba pro čtení
):
    """Získá detail konkrétního itemu."""
    db_item = get_item_or_404(db, item_id=item_id)
    # TODO: Přidat oprávnění pro čtení? (např. člen světa/kampaně)
    return db_item

@router.get("/", response_model=List[schemas.Item])
def read_items(
    *,
    db: Session = Depends(get_db),
    world_id: int = Query(..., description="ID světa pro filtrování itemů"),
    character_id: Optional[int] = Query(None, description="Filtrovat itemy podle ID postavy"),
    location_id: Optional[int] = Query(None, description="Filtrovat itemy podle ID lokace"),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(get_current_user) # Zatím není potřeba pro čtení
):
    """Získá seznam itemů pro daný svět, volitelně filtrovaný."""
    # TODO: Přidat oprávnění pro čtení? (např. člen světa/kampaně)
    # Ověříme alespoň existenci světa
    world = crud.get_world(db, world_id=world_id)
    if not world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")
    
    items = crud.get_items_by_world(
        db, 
        world_id=world_id, 
        character_id=character_id, 
        location_id=location_id, 
        skip=skip, 
        limit=limit
    )
    return items

@router.put("/{item_id}", response_model=schemas.Item)
async def update_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    item_in: schemas.ItemUpdate,
    current_user: models.User = Depends(get_current_user),
):
    """Aktualizuje item. Vyžaduje vlastnictví světa."""
    db_item = get_item_or_404(db, item_id=item_id)
    
    # Ověření, že uživatel vlastní svět, do kterého item patří
    await verify_world_owner(world_id=db_item.world_id, current_user=current_user, db=db)
    
    # Validace nových character_id a location_id (pokud se mění)
    update_data = item_in.dict(exclude_unset=True)
    new_character_id = update_data.get("character_id")
    new_location_id = update_data.get("location_id")
    # Pokud je v update_data explicitně None, také validujeme (pro odebrání)
    if "character_id" in update_data or "location_id" in update_data:
        await validate_item_relations(
            db=db,
            world_id=db_item.world_id,
            character_id=new_character_id if new_character_id is not None else item_in.character_id, # Pass original if not in update_data
            location_id=new_location_id if new_location_id is not None else item_in.location_id
        )

    item = crud.update_item(db=db, db_item=db_item, item_in=item_in)
    return item

@router.delete("/{item_id}", response_model=schemas.Item)
async def delete_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: models.User = Depends(get_current_user),
):
    """Smaže item. Vyžaduje vlastnictví světa."""
    db_item = get_item_or_404(db, item_id=item_id)
    
    # Ověření, že uživatel vlastní svět, do kterého item patří
    await verify_world_owner(world_id=db_item.world_id, current_user=current_user, db=db)
    
    item = crud.delete_item(db=db, db_item=db_item)
    return item 