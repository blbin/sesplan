from fastapi import APIRouter

from .endpoints import (
    login, 
    users, 
    worlds, 
    campaigns, 
    characters, 
    campaign_invites, 
    user_campaigns,
    journals, 
    journal_entries,
    sessions,
    locations,
    items,
    availability,
    events  # Import nového endpointu
)

api_router = APIRouter()

# Připojení jednotlivých routerů
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users") # Odebráno tags=["users"]
api_router.include_router(worlds.router, prefix="/worlds", tags=["worlds"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"]) # Vnořené pod /worlds?
api_router.include_router(characters.router, prefix="/characters", tags=["characters"])
api_router.include_router(campaign_invites.router, prefix="/invites", tags=["campaign-invites"])
api_router.include_router(user_campaigns.router, prefix="/user-campaigns", tags=["user-campaigns"])
api_router.include_router(journals.router, prefix="/journals", tags=["journals"])
api_router.include_router(journal_entries.router, prefix="/journal-entries", tags=["journal-entries"]) # prefix byl už definován v endpointu
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"]) # Vnořené pod /campaigns?
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(availability.router, prefix="/availability", tags=["availability"])

# Vnoření Event routeru pod World router
# POZOR: Campaigns, Sessions, Locations, Items by také měly být pravděpodobně vnořené!
# Prozatím vnoříme jen Events.
worlds.router.include_router(events.router, prefix="/{world_id}/events", tags=["events"])

# TODO: Zrevidovat strukturu prefixů a vnoření routerů pro konzistenci (např. /worlds/{world_id}/campaigns/{campaign_id}/sessions) 