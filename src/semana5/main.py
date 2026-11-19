"""Semana 5 — Microservicio RESTful (FastAPI) que se prueba dentro de contenedores.

Componente del sistema de crédito: API de clientes del banco.

Endpoints:
    GET /health                    -> healthcheck para Docker Compose
    GET /api/v1/clientes           -> lista de clientes (validada con JSON Schema)
    GET /api/v1/clientes/{id}      -> cliente por ID o 404
"""

from fastapi import FastAPI, HTTPException

app = FastAPI(title="api-clientes", version="1.0.0")

# Base de datos simulada en memoria
CLIENTES_DB = [
    {"id": 1, "nombre": "Carlos Perez", "documento": "1012345678", "score": 720, "activo": True},
    {"id": 2, "nombre": "Ana Gomez", "documento": "1098765432", "score": 580, "activo": False},
]


# Endpoint 1: Healthcheck para monitoreo del contenedor
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "api-clientes"}


# Endpoint 2: Listar todos los clientes
@app.get("/api/v1/clientes")
def get_clientes():
    return CLIENTES_DB


# Endpoint 3: Consultar cliente por ID
@app.get("/api/v1/clientes/{cliente_id}")
def get_cliente(cliente_id: int):
    cliente = next((c for c in CLIENTES_DB if c["id"] == cliente_id), None)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente
