"""Semana 6 — Prueba del servicio base de crédito con TestClient (se ejecuta en el pipeline de CI)."""

from fastapi.testclient import TestClient

from src.semana6.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Servicio de crédito funcionando"}


def test_ruta_inexistente_devuelve_404():
    response = client.get("/no-existe")
    assert response.status_code == 404
