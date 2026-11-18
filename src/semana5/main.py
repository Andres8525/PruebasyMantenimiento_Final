"""Semana 5 — Microservicio RESTful (FastAPI) que se prueba dentro de contenedores.

Endpoints:
    GET /health                 -> healthcheck para Docker Compose
    GET /api/v1/users           -> lista de usuarios (validada con JSON Schema)
    GET /api/v1/users/{user_id} -> usuario por ID o 404
"""

from fastapi import FastAPI, HTTPException

app = FastAPI(title="user-api", version="1.0.0")

# Base de datos simulada en memoria
USERS_DB = [
    {"id": 1, "name": "Carlos Perez", "email": "carlos@example.com", "active": True},
    {"id": 2, "name": "Ana Gomez", "email": "ana@example.com", "active": False},
]


# Endpoint 1: Healthcheck para monitoreo del contenedor
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "user-api"}


# Endpoint 2: Listar todos los usuarios
@app.get("/api/v1/users")
def get_users():
    return USERS_DB


# Endpoint 3: Consultar usuario por ID
@app.get("/api/v1/users/{user_id}")
def get_user(user_id: int):
    user = next((u for u in USERS_DB if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
