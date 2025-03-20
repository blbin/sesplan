from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings
from app.db.session import Base, engine
from app.models.user import User

print("Dostupné tabulky před vytvořením:", Base.metadata.tables.keys())
Base.metadata.create_all(bind=engine)
print("Dostupné tabulky po vytvoření:", Base.metadata.tables.keys())

app = FastAPI(title="Sesplan API")
app.include_router(api_router, prefix="/V1")

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

