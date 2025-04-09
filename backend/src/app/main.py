from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.core.config import settings
# from app.db.session import Base, engine
from app.db.session import engine # Potřebujeme engine pro Alembic v jiném kontextu, Base pro modely
from app import models  # Import the models package

print("Importované modely:", models.__all__)

# Ensure all models are imported before creating tables
# print("Dostupné tabulky před vytvořením:", Base.metadata.tables.keys())
# Base.metadata.create_all(bind=engine)
# print("Dostupné tabulky po vytvoření:", Base.metadata.tables.keys())

app = FastAPI(title="Sesplan API")

# Přidání CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://{settings.DOMAIN}",
        f"https://{settings.DOMAIN}",
        "http://localhost:5173",
        "https://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/V1")

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

