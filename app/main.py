"""
Punto de entrada principal de la API Edu-vida.
"""

from fastapi import FastAPI
from app.database import init_db

# 👇 Importamos todos los routers aquí arriba 👇
from app.api.users import router as users_router
from app.api.moods import router as moods_router

# Creamos la instancia de FastAPI
app = FastAPI(
    title="Edu-vida API",
    description="API para gestionar el bienestar emocional de estudiantes",
    version="1.0.0"
)

# Evento que se ejecuta al iniciar el servidor: crea las tablas en la BD
@app.on_event("startup")
def on_startup():
    init_db()

# Conectamos los routers a la app principal
app.include_router(users_router)
app.include_router(moods_router)

@app.get("/")
def root():
    return {"app": "Edu-vida", "status": "ok"}