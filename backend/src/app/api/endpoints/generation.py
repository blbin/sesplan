from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.orm import Session
from typing import Any, List, Dict, Union

from app.api import dependencies
from app.core.config import settings # Přidán import settings
from app.services.langchain_service import langchain_service
from app.models import User, World
from app import schemas # Import schemas to use for response_model
# Import Pydantic schemas if needed later, e.g.:
# from app.schemas.generation import GenerateEntityRequest, SummarizeSessionRequest

# Import limiteru z main aplikace
# Potřebujeme přístup k instanci limiteru definované v main.py
# Správný způsob je předat ji přes závislost nebo použít globální instanci (méně ideální)
# Pro jednoduchost použijeme instanci z main, i když to vytváří závislost
# Poznámka: Toto vyžaduje, aby main.py byl importovatelný a limiter byl definován na úrovni modulu.
# from app.main import limiter # Přidán import limiteru <-- Toto způsobovalo circular import
from app.core.limiter import limiter # Import opraven na app.core.limiter

# Definice možných návratových typů pro response_model
ResponseType = Union[schemas.Character, schemas.Location, schemas.Organization, schemas.Item]

router = APIRouter()

@router.post("/worlds/{world_id}/generate/{entity_type}", response_model=ResponseType)
@limiter.limit(settings.AI_REQUEST_LIMITS) # Použití spojených limitů z configu
async def generate_new_entity(
    *,
    request: Request, # Přidáno pro přístup k limiteru/request state
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_user),
    world_id: int, # Added world_id from path
    entity_type: str,
    # Optional: Add dependency to check if world exists and user has access
    # world: World = Depends(dependencies.get_world_for_user(required=True)), # Example dependency
    existing_entities: List[Dict[str, Any]] = Body(...),
    context: str | None = Body(None)
) -> Any:
    """
    Generates a new game entity within a specific world using LangChain, saves it, and returns the created entity.
    Requires authentication.
    """
    if not entity_type:
        raise HTTPException(status_code=400, detail="Entity type cannot be empty.")

    # TODO: Add check if user has rights to generate entities in this world_id
    # This might be part of the get_world_for_user dependency or checked manually.

    try:
        created_entity = await langchain_service.generate_entity(
            db=db,
            current_user=current_user,
            world_id=world_id, # Pass world_id
            entity_type=entity_type,
            existing_entities=existing_entities,
            context=context
        )
        # Vracíme přímo SQLAlchemy objekt, FastAPI ho serializuje pomocí response_model
        return created_entity
    except ValueError as ve:
        # Catch specific errors from the service (like parsing or validation)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # TODO: Add more specific error handling
        # Přidáme detail chyby pro lepší diagnostiku
        import traceback
        print(f"Error during entity generation: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate and save entity: {str(e)}")

@router.post("/summarize/session", response_model=str)
@limiter.limit(settings.AI_REQUEST_LIMITS) # Použití spojených limitů z configu
async def summarize_game_session(
    *,
    request: Request, # Přidáno pro přístup k limiteru/request state
    # db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_user),
    session_data: Dict[str, Any] = Body(...), # Data about the session
    journal_entries: List[Dict[str, Any]] = Body(...) # Related journal entries
) -> Any:
    """
    Summarizes a game session using LangChain based on session data and journal entries.
    Requires authentication.
    """
    try:
        summary = await langchain_service.summarize_session(
            session_data=session_data,
            journal_entries=journal_entries
        )
        return summary
    except Exception as e:
        # TODO: Add more specific error handling
        raise HTTPException(status_code=500, detail=f"Failed to summarize session: {str(e)}") 