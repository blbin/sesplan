from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.core.config import settings
# from app.db.session import Base, engine
from app.db.session import engine, Base # Zajistíme import Base
from app import models  # Import the models package

#print("Importované modely:", models.__all__)

# Ensure all models are imported before creating tables
#print("Dostupné tabulky před vytvořením:", Base.metadata.tables.keys())
Base.metadata.create_all(bind=engine) # Odkomentováno pro synchronizaci DB
#print("DB sync: Tables created/checked based on models.") # Přidáme log pro potvrzení
#print("Dostupné tabulky po vytvoření:", Base.metadata.tables.keys())

app = FastAPI(title="Sesplan API", redirect_slashes=False)

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


app.include_router(api_router, prefix="/V1")

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}
