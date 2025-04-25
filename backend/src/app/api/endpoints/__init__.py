from fastapi import APIRouter

# Importujte zde jednotlivé routery z tohoto adresáře
from . import auth
from . import base
from . import users
from . import worlds
from . import campaigns
from . import characters
from . import campaign_invites
from . import journals
from . import journal_entries
from . import sessions
from . import locations
# Import routeru pro itemy
from . import items
# Import routeru pro availability
from . import availability
# Import routeru pro organizations
from . import organizations
# Import routeru pro location_tag_types
from . import location_tag_types
# Import routerů pro character tags
from . import character_tag_types
from . import character_tags
# Import routerů pro item tags
from . import item_tag_types
from . import item_tags
# Import routeru pro organization tag types
from . import organization_tag_types

router = APIRouter()

# Zahrňte routery do hlavního routeru
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(base.router, tags=["base"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(worlds.router, prefix="/worlds", tags=["worlds"])
router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
router.include_router(characters.router, prefix="/characters", tags=["characters"])
router.include_router(journals.router, prefix="/journals", tags=["journals"])
router.include_router(journal_entries.router)
router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
router.include_router(locations.router, prefix="/locations", tags=["locations"])
# Přidání routeru pro itemy
router.include_router(items.router, prefix="/items", tags=["items"])
# Přidání routeru pro organizations
router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
# Přidání routeru pro location_tag_types
router.include_router(location_tag_types.router, prefix="/worlds/{world_id}/location-tag-types", tags=["location-tag-types"])
# Přidání routeru pro character_tag_types
router.include_router(character_tag_types.router, prefix="/worlds/{world_id}/character-tag-types", tags=["character-tag-types"])
# Přidání routeru pro character_tags
router.include_router(character_tags.router, prefix="/characters/{character_id}/tags", tags=["character-tags"])
# Přidání routeru pro item_tag_types
router.include_router(item_tag_types.router, prefix="/worlds/{world_id}/item-tag-types", tags=["item-tag-types"])
# Přidání routeru pro item_tags
router.include_router(item_tags.router, prefix="/items/{item_id}/tags", tags=["item-tags"])
# Přidání routeru pro organization_tag_types
router.include_router(
    organization_tag_types.router, 
    prefix="/worlds/{world_id}/organization-tag-types", 
    tags=["organization-tag-types"]
)

# Attach the availability router directly to the main router
router.include_router(
    availability.router, 
    prefix="/sessions/{session_id}/availabilities", 
    tags=["availability"]
)

# Registrace obecného routeru pro pozvánky (přijetí/smazání)
router.include_router(
    campaign_invites.invite_router,
    prefix="/invites",
    tags=["invites"]
)

# Přidejte další endpointy z původního endpoints.py
@router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}