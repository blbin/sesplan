from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.api.users import router as users_router
from app.core.config import settings
from app.db.session import Base, engine
from app.models.user import User

print("Dostupné tabulky před vytvořením:", Base.metadata.tables.keys())
Base.metadata.create_all(bind=engine)
print("Dostupné tabulky po vytvoření:", Base.metadata.tables.keys())

app = FastAPI(title="Sesplan API")
app.include_router(api_router, prefix="/api")
app.include_router(users_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}


