"""Semana 5 — Pruebas de API REST: estado HTTP, cabeceras/tiempos y contrato JSON Schema."""

import requests
from jsonschema import validate

# Esquema JSON requerido para cada objeto de usuario (contrato con el cliente)
USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string"},
        "active": {"type": "boolean"},
    },
    "required": ["id", "name", "email", "active"],
}

TIEMPO_MAXIMO_SEGUNDOS = 1.0


# --- Nivel 1: Código de estado HTTP ---
def test_health_check_returns_200(base_url):
    response = requests.get(f"{base_url}/health", timeout=5)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_non_existing_user_returns_404(base_url):
    response = requests.get(f"{base_url}/api/v1/users/999", timeout=5)
    assert response.status_code == 404


# --- Nivel 2: Tiempos y cabeceras ---
def test_users_content_type_is_json(base_url):
    response = requests.get(f"{base_url}/api/v1/users", timeout=5)
    assert response.headers["Content-Type"].startswith("application/json")


def test_users_response_time_within_threshold(base_url):
    response = requests.get(f"{base_url}/api/v1/users", timeout=5)
    assert response.elapsed.total_seconds() < TIEMPO_MAXIMO_SEGUNDOS


# --- Nivel 3: Contrato de datos (JSON Schema) ---
def test_get_users_schema_validation(base_url):
    response = requests.get(f"{base_url}/api/v1/users", timeout=5)
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    for user in users:
        validate(instance=user, schema=USER_SCHEMA)


def test_get_user_by_id_schema_validation(base_url):
    response = requests.get(f"{base_url}/api/v1/users/1", timeout=5)
    assert response.status_code == 200
    validate(instance=response.json(), schema=USER_SCHEMA)
