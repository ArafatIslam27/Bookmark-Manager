from contextlib import asynccontextmanager
from fastapi import FastAPI
from bookmark_manager.api.routes import router
from bookmark_manager.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Everything here runs BEFORE the server starts accepting requests
    init_db()
    yield
    # Everything here runs AFTER the server shuts down

app = FastAPI(title="Modern Bookmark API", lifespan=lifespan)

# Register our routes
app.include_router(router)

@app.get("/")
async def root():
    return {"status": "healthy", "service": "Bookmark Manager"}