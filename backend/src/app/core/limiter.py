from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models import User # Import User modelu pro typování
from app.core.config import settings # Import settings pro REDIS_URL
import redis.asyncio as redis

# Funkce pro získání klíče (uživatelské ID nebo IP)
async def get_limiter_key(request: Request) -> str:
    # Pokusíme se získat uživatele z request.state (pokud ho tam auth middleware přidává)
    user: User | None = getattr(request.state, "user", None)
    if user:
        return str(user.id)
    # Fallback na IP adresu, pokud uživatel není dostupný v request.state
    return get_remote_address(request)

# Inicializace limiteru s vlastní key func a Redis storage
limiter = Limiter(key_func=get_limiter_key, storage_uri=settings.REDIS_URL)

# Funkce pro asynchronní inicializaci Redis spojení pro limiter
# async def startup_limiter():
    # Poznámka: slowapi >= 0.1.8 umožňuje přímé předání async redis instance
    # Pro starší verze nebo pro jistotu použijeme URL string
    # redis_pool = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    # await limiter.init(redis_pool) # Pokud bychom chtěli předat instanci
    # await limiter.startup(f"redis://{settings.REDIS_URL}") # Použijeme URL

# async def shutdown_limiter():
#     await limiter.shutdown() 