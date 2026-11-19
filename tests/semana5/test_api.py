"""Semana 5 — Pruebas de la API de clientes: estado HTTP, cabeceras/tiempos y contrato JSON Schema."""

import requests
from jsonschema import validate

# Esquema JSON requerido para cada cliente (contrato con los canales del banco)
CLIENTE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "nombre": {"type": "string"},
        "documento": {"type": "string"},
        "score": {"type": "integer", "minimum": 300, "maximum": 850},
        "activo": {"type": "boolean"},
    },
    "required": ["id", "nombre", "documento", "score", "activo"],
}

TIEMPO_MAXIMO_SEGUNDOS = 1.0


# --- Nivel 1: Código de estado HTTP ---
def test_health_check_returns_200(base_url):
    response = requests.get(f"{base_url}/health", timeout=5)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_cliente_inexistente_returns_404(base_url):
    response = requests.get(f"{base_url}/api/v1/clientes/999", timeout=5)
    assert response.status_code == 404


# --- Nivel 2: Tiempos y cabeceras ---
def test_clientes_content_type_is_json(base_url):
    response = requests.get(f"{base_url}/api/v1/clientes", timeout=5)
    assert response.headers["Content-Type"].startswith("application/json")


def test_clientes_response_time_within_threshold(base_url):
    response = requests.get(f"{base_url}/api/v1/clientes", timeout=5)
    assert response.elapsed.total_seconds() < TIEMPO_MAXIMO_SEGUNDOS


# --- Nivel 3: Contrato de datos (JSON Schema) ---
def test_clientes_schema_validation(base_url):
    response = requests.get(f"{base_url}/api/v1/clientes", timeout=5)
    assert response.status_code == 200
    clientes = response.json()
    assert isinstance(clientes, list)
    for cliente in clientes:
        validate(instance=cliente, schema=CLIENTE_SCHEMA)


def test_cliente_por_id_schema_validation(base_url):
    response = requests.get(f"{base_url}/api/v1/clientes/1", timeout=5)
    assert response.status_code == 200
    validate(instance=response.json(), schema=CLIENTE_SCHEMA)
