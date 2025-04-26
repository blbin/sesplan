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
    organizations,
    items,
    availability,
    events,
    location_tag_types,
    generation,
    base,
    character_tag_types,
    character_tags,
    item_tag_types,
    item_tags,
    organization_tag_types
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

# Add organization router
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])

# LangChain / AI Endpoints
api_router.include_router(generation.router, prefix="/ai", tags=["ai"])

# Base router (pro healthcheck)
api_router.include_router(base.router, tags=["base"])

# Obecný router pro pozvánky (přijetí/smazání)
api_router.include_router(
    campaign_invites.invite_router,
    prefix="/invites",
    tags=["invites"]
)

# Vnoření Event routeru pod World router
# POZOR: Campaigns, Sessions, Locations, Items by také měly být pravděpodobně vnořené!
# Prozatím vnoříme jen Events.
worlds.router.include_router(events.router, prefix="/{world_id}/events", tags=["events"])

# Vnoření specifických routerů pod Worlds
worlds.router.include_router(
    location_tag_types.router, 
    prefix="/{world_id}/location-tag-types", 
    tags=["location-tag-types"]
)
worlds.router.include_router(
    character_tag_types.router, 
    prefix="/{world_id}/character-tag-types", 
    tags=["character-tag-types"]
)
worlds.router.include_router(
    item_tag_types.router, 
    prefix="/{world_id}/item-tag-types", 
    tags=["item-tag-types"]
)
worlds.router.include_router(
    organization_tag_types.router, 
    prefix="/{world_id}/organization-tag-types", 
    tags=["organization-tag-types"]
)

# Vnoření pod Characters
characters.router.include_router(
    character_tags.router, 
    prefix="/{character_id}/tags", 
    tags=["character-tags"]
)

# Vnoření pod Items
items.router.include_router(
    item_tags.router, 
    prefix="/{item_id}/tags", 
    tags=["item-tags"]
)

# TODO: Zrevidovat strukturu prefixů a vnoření routerů pro konzistenci (např. /worlds/{world_id}/campaigns/{campaign_id}/sessions) 