from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from bookmark_manager.api.routes import router
from bookmark_manager.database import init_db
from pathlib import Path
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Production Bookmark Service", lifespan=lifespan)
app.include_router(router)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Bookmark Manager"}