from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, models, schemas
from app.api import dependencies
from app.db.session import get_db
from app.auth.auth import get_current_user
from app.schemas.organization_tag import OrganizationTag

router = APIRouter()

@router.post("/", response_model=schemas.Organization, status_code=status.HTTP_201_CREATED)
async def create_organization(
    *,
    db: Session = Depends(get_db),
    organization_in: schemas.OrganizationCreate,
    current_user: models.User = Depends(get_current_user)
):
    """Create a new organization within a specific world. User must own the world."""
    # Verify ownership before creating
    await dependencies.verify_world_owner(world_id=organization_in.world_id, current_user=current_user, db=db)

    # Verify parent_organization_id if provided
    if organization_in.parent_organization_id:
        parent_organization = crud.get_organization(db, organization_id=organization_in.parent_organization_id)
        if not parent_organization or parent_organization.world_id != organization_in.world_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parent_organization_id for this world")

    organization = crud.create_organization(db=db, organization=organization_in)
    return organization

@router.get("/{organization_id}", response_model=schemas.Organization)
async def read_organization(
    *,
    db: Session = Depends(get_db),
    organization_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific organization by ID. User must be a member of the world."""
    db_organization = crud.get_organization(db, organization_id=organization_id)
    if db_organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Verify membership (using the existing non-async function)
    dependencies.check_world_membership(world_id=db_organization.world_id, user_id=current_user.id, db=db)

    return db_organization

@router.get("/", response_model=List[schemas.Organization])
async def read_organizations_by_world(
    *,
    db: Session = Depends(get_db),
    world_id: int = Query(..., description="Filter organizations by world ID"),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve organizations belonging to a specific world. User must be a member."""
    # Verify membership (using the existing non-async function)
    dependencies.check_world_membership(world_id=world_id, user_id=current_user.id, db=db)

    organizations = crud.get_organizations_by_world(db, world_id=world_id, skip=skip, limit=limit)
    return organizations

@router.put("/{organization_id}", response_model=schemas.Organization)
async def update_organization(
    *,
    db: Session = Depends(get_db),
    organization_id: int,
    organization_in: schemas.OrganizationUpdate,
    current_user: models.User = Depends(get_current_user)
):
    """Update an organization. User must own the world the organization belongs to."""
    db_organization = crud.get_organization(db, organization_id=organization_id)
    if not db_organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Verify ownership of the world the organization belongs to
    await dependencies.verify_world_owner(world_id=db_organization.world_id, current_user=current_user, db=db)

    # Verify new parent_organization_id if provided
    if organization_in.parent_organization_id is not None:
        if organization_in.parent_organization_id == db_organization.id:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization cannot be its own parent")
        parent_organization = crud.get_organization(db, organization_id=organization_in.parent_organization_id)
        if not parent_organization or parent_organization.world_id != db_organization.world_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parent_organization_id for this world")

    organization = crud.update_organization(db=db, db_organization=db_organization, organization_in=organization_in)
    return organization

@router.delete("/{organization_id}", response_model=schemas.Organization)
async def delete_organization(
    *,
    db: Session = Depends(get_db),
    organization_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """Delete an organization. User must own the world the organization belongs to."""
    db_organization = crud.get_organization(db, organization_id=organization_id)
    if not db_organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Verify ownership of the world
    await dependencies.verify_world_owner(world_id=db_organization.world_id, current_user=current_user, db=db)

    # Before deleting, check if it's a parent to other organizations
    # Depending on requirements, either prevent deletion or handle children (e.g., set parent_id to null)
    # The model currently uses ondelete="SET NULL" for parent_organization_id, so children should be handled by DB.

    deleted_organization_data = schemas.Organization.from_orm(db_organization) # Capture data before deletion
    crud.delete_organization(db=db, db_organization=db_organization)

    # Return the data of the deleted object
    return deleted_organization_data
    # Alternatively, return status 204 No Content:
    # return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Endpoints for managing organization tags ---

@router.post(
    "/{organization_id}/tags/{tag_type_id}", 
    response_model=schemas.OrganizationTag, # Vrátíme vytvořené přiřazení
    status_code=status.HTTP_201_CREATED,
    summary="Přiřadit tag k organizaci"
)
async def add_tag_to_organization_endpoint(
    organization_id: int = Path(..., description="ID organizace"),
    tag_type_id: int = Path(..., description="ID typu tagu, který se má přiřadit"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Přiřadí existující typ tagu ke konkrétní organizaci. Vyžaduje vlastnictví světa organizace."""
    # 1. Získáme organizaci (pro ověření vlastnictví světa)
    db_organization = crud.get_organization(db, organization_id=organization_id)
    if not db_organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # 2. Ověříme vlastnictví světa
    await dependencies.verify_world_owner(world_id=db_organization.world_id, current_user=current_user, db=db)

    # 3. CRUD operace pro přidání tagu (ta obsahuje validaci tag_type_id a world_id)
    try:
        # Předáme db, organization_id, tag_type_id
        db_association = crud.add_tag_to_organization(db=db, organization_id=organization_id, tag_type_id=tag_type_id)
        # Načtení tag_type probíhá uvnitř CRUD funkce, pokud je potřeba pro response model
    except ValueError as e:
        # Chyby z CRUD (nenalezeno, jiný svět) převedeme na HTTP chyby
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
            
    return db_association

@router.delete(
    "/{organization_id}/tags/{tag_type_id}", 
    status_code=status.HTTP_204_NO_CONTENT, # Standardní odpověď pro úspěšné smazání
    summary="Odebrat tag z organizace"
)
async def remove_tag_from_organization_endpoint(
    organization_id: int = Path(..., description="ID organizace"),
    tag_type_id: int = Path(..., description="ID typu tagu, který se má odebrat"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Odebere přiřazení typu tagu od konkrétní organizace. Vyžaduje vlastnictví světa organizace."""
    # 1. Získáme organizaci (pro ověření vlastnictví světa)
    db_organization = crud.get_organization(db, organization_id=organization_id)
    if not db_organization:
        # Pokud organizace neexistuje, tag stejně nemůže být přiřazen
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # 2. Ověříme vlastnictví světa
    await dependencies.verify_world_owner(world_id=db_organization.world_id, current_user=current_user, db=db)

    # 3. CRUD operace pro odebrání tagu
    deleted = crud.remove_tag_from_organization(db=db, organization_id=organization_id, tag_type_id=tag_type_id)
    
    if not deleted:
        # Pokud nebylo nic smazáno, znamená to, že tag nebyl k organizaci přiřazen
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not associated with this organization")

    # Při úspěchu nevracíme žádný obsah (status 204)
    return 