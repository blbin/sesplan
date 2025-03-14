from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings

app = FastAPI(title="Sesplan API")
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}
