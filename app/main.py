"""
Punto de entrada de la API Edu-vida.
"""
from fastapi import FastAPI
from app.app.database import init_db

app = FastAPI(title="Edu-vida API", version="0.1.0")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"app": "Edu-vida", "status": "ok"}

