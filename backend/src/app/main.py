from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.core.config import settings
# from app.db.session import Base, engine
from app.db.session import engine, Base # Zajistíme import Base
from app import models  # Import the models package

# --- Rate Limiting Imports ---
from slowapi import _rate_limit_exceeded_handler # Import handleru
from slowapi.errors import RateLimitExceeded # Import výjimky
from slowapi.middleware import SlowAPIMiddleware # Import middleware
# Importujeme pouze limiter, ne startup/shutdown funkce
from app.core.limiter import limiter # Import z nového modulu

# --- End Rate Limiting Imports ---


#print("Importované modely:", models.__all__)

# Ensure all models are imported before creating tables
#print("Dostupné tabulky před vytvořením:", Base.metadata.tables.keys())
Base.metadata.create_all(bind=engine) # Odkomentováno pro synchronizaci DB
#print("DB sync: Tables created/checked based on models.") # Přidáme log pro potvrzení
#print("Dostupné tabulky po vytvoření:", Base.metadata.tables.keys())

app = FastAPI(
    title="Sesplan API",
    redirect_slashes=False,
    # Přidání lifecycle events pro limiter z app.core.limiter <-- ODSTRANĚNO
    # on_startup=[startup_limiter],
    # on_shutdown=[shutdown_limiter]
)

# Nastavení handleru pro výjimku RateLimitExceeded (používáme importovaný handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Přidání SlowAPI middleware (používáme importovaný middleware)
app.add_middleware(SlowAPIMiddleware) # <-- ZNOVU POVOLENO

# Přidání CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"https://{settings.DOMAIN}",
        "http://localhost:5173",
        "https://localhost:5173",
        "http://localhost",
        "https://localhost"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

# Inject limiter instance into the app state for dependency injection
app.state.limiter = limiter # <-- TOTO JE POTŘEBA ODKOMENTOVAT

app.include_router(api_router, prefix="/V1")

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}
