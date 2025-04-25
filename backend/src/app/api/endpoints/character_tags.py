from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
import sqlalchemy.orm
from typing import List

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
from ..dependencies import get_character_or_404, verify_character_permission

router = APIRouter()

# Tento router bude pravděpodobně součástí routeru pro charaktery, 
# takže prefix bude /characters/{character_id}/tags

@router.post(
    "/{tag_type_id}", 
    response_model=schemas.CharacterTag, 
    status_code=status.HTTP_201_CREATED, 
    summary="Přidat tag k charakteru"
)
async def add_tag_to_character_endpoint(
    *, 
    character_id: int, # Získáno z prefixu nadřazeného routeru
    tag_type_id: int = Path(..., description="ID typu tagu charakteru, který se má přidat"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    # Ověření, že charakter existuje a uživatel má práva ho upravit
    _=Depends(verify_character_permission) # verify_character_permission použije character_id z prefixu
):
    """Přidá specifický typ tagu k charakteru."""
    try:
        # Samotné CRUD operace by měly ověřit, že tag type patří ke správnému světu
        db_tag = crud.add_tag_to_character(db=db, character_id=character_id, tag_type_id=tag_type_id)
    except ValueError as e:
        # Může nastat, pokud CRUD vyhodí ValueError (např. nekompatibilní svět)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as e:
        # Propagujeme HTTP výjimky z CRUD (např. 404 pro tag type)
        raise e
        
    # Načteme přiřazení tagu včetně detailů tag_type pro response
    db_tag_with_details = db.query(models.CharacterTag).options(
        sqlalchemy.orm.joinedload(models.CharacterTag.tag_type)
    ).filter(models.CharacterTag.id == db_tag.id).first()
    
    return db_tag_with_details

@router.delete(
    "/{tag_type_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Odebrat tag z charakteru"
)
async def remove_tag_from_character_endpoint(
    *, 
    character_id: int, # Získáno z prefixu nadřazeného routeru
    tag_type_id: int = Path(..., description="ID typu tagu charakteru, který se má odebrat"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    # Ověření, že charakter existuje a uživatel má práva ho upravit
    _=Depends(verify_character_permission)
):
    """Odebere specifický typ tagu z charakteru."""
    deleted_tag = crud.remove_tag_from_character(db=db, character_id=character_id, tag_type_id=tag_type_id)
    if not deleted_tag:
        # CRUD nevrátil nic, protože tag nebyl nalezen/přiřazen
        # Můžeme vrátit 404 nebo nechat 204 (protože výsledný stav je stejný - tag není přiřazen)
        # Pro konzistenci smazání, necháme 204
        pass 
    # Není potřeba vracet tělo odpovědi při statusu 204
    return None

# Poznámka: Endpoint pro GET /characters/{character_id}/tags 
# by měl být součástí character endpointu, který vrací detaily charakteru, 
# kde budou tagy zahrnuty v odpovědi (jak je definováno v Character modelu a schématu). 