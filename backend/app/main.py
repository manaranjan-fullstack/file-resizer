import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes.resize import router as resize_router

app = FastAPI(title="Universal File Resizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(resize_router, prefix="/api")

frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")