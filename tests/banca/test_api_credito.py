"""Caso de uso: Banca — contrato de la API del servicio de crédito."""

import pytest
from fastapi.testclient import TestClient
from jsonschema import validate

from src.banca.api import app

client = TestClient(app)

RESPUESTA_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {"enum": ["APROBADO", "RECHAZADO"]},
        "motivos": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "score": {"type": "integer"},
        "ingresos": {"type": "number"},
        "politica": {"type": "string"},
    },
    "required": ["decision", "motivos", "score", "ingresos", "politica"],
}


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_politica_vigente():
    respuesta = client.get("/api/v1/creditos/politica")
    assert respuesta.status_code == 200
    assert respuesta.json()["score_minimo_aprobacion"] == 600


@pytest.mark.parametrize(
    "score, ingresos, decision",
    [(600, 2000, "APROBADO"), (599, 2500.0, "RECHAZADO"), (700, 1999.99, "RECHAZADO")],
)
def test_evaluar_cumple_contrato(score, ingresos, decision):
    respuesta = client.post("/api/v1/creditos/evaluar", json={"score": score, "ingresos": ingresos})
    assert respuesta.status_code == 200
    validate(instance=respuesta.json(), schema=RESPUESTA_SCHEMA)
    assert respuesta.json()["decision"] == decision


@pytest.mark.parametrize(
    "payload",
    [
        {"score": 851, "ingresos": 3000},    # fuera del dominio del score
        {"score": 700, "ingresos": -1},      # ingresos negativos
        {"score": "700", "ingresos": 2500},  # tipo incorrecto
        {"score": 700},                      # campo faltante
    ],
)
def test_evaluar_rechaza_solicitudes_invalidas(payload):
    assert client.post("/api/v1/creditos/evaluar", json=payload).status_code == 422
