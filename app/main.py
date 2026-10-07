from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import BASE_DIR
from .routers import chat, run, student

app = FastAPI(title="Algo mentor", version="1.0.0")

app.include_router(chat.router)
app.include_router(run.router)
app.include_router(student.router)

FRONTEND_DIST = BASE_DIR / "frontend" / "dist"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIST / "index.html")


app.mount(
    "/assets",
    StaticFiles(directory=FRONTEND_DIST / "assets"),  # build Vite (React)
    name="assets",
)
