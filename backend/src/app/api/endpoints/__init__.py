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