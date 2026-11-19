"""Semana 9 — Pruebas del pipeline de CD: health check, Caso A, Caso B,
servidor caído, enmascarado del secreto y telemetría a Telegram (sin red real).
"""

import pytest
import requests
from fastapi.testclient import TestClient

from src.semana9 import deploy, main
from src.semana9.main import app

client = TestClient(app)


class _Respuesta:
    def __init__(self, status_code):
        self.status_code = status_code


# --- API de Staging ---
def test_root_online():
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert respuesta.json()["status"] == "online"


def test_health_saludable(monkeypatch):
    monkeypatch.setattr(main, "IS_HEALTHY", True)
    respuesta = client.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "healthy", "version": "1.0.0"}


def test_health_enfermo_devuelve_500(monkeypatch):
    monkeypatch.setattr(main, "IS_HEALTHY", False)
    respuesta = client.get("/health")
    assert respuesta.status_code == 500
    assert respuesta.json()["status"] == "unhealthy"


# --- Secretos ---
@pytest.mark.parametrize(
    "secreto, esperado",
    [("default_secret_dev", "def***"), ("abc", "abc***"), ("", "(vacío)")],
)
def test_enmascarar_no_expone_el_secreto(secreto, esperado):
    assert deploy.enmascarar(secreto) == esperado


def test_pipeline_no_imprime_el_secreto(monkeypatch, capsys):
    monkeypatch.setattr(deploy.requests, "get", lambda url, timeout: _Respuesta(200))
    deploy.ejecutar_pipeline("http://staging/health", "super_secreto_123", notificar=lambda m: False)
    assert "super_secreto_123" not in capsys.readouterr().out


# --- Caso A, Caso B y servidor inaccesible ---
def test_caso_a_promociona_a_produccion(monkeypatch):
    enviados = []
    monkeypatch.setattr(deploy.requests, "get", lambda url, timeout: _Respuesta(200))
    registro = deploy.ejecutar_pipeline("http://staging/health", "s3cr3t", notificar=enviados.append)
    assert registro["resultado"] == deploy.PROMOCIONADO
    assert registro["http"] == 200
    assert "DESPLIEGUE EXITOSO" in enviados[0]


def test_caso_b_rollback_ante_http_500(monkeypatch):
    enviados = []
    monkeypatch.setattr(deploy.requests, "get", lambda url, timeout: _Respuesta(500))
    registro = deploy.ejecutar_pipeline("http://staging/health", "s3cr3t", notificar=enviados.append)
    assert registro["resultado"] == deploy.ROLLBACK
    assert registro["http"] == 500
    assert "ROLLBACK AUTOMÁTICO" in enviados[0] and "HTTP 500" in enviados[0]


def test_servidor_inaccesible_activa_rollback(monkeypatch):
    def sin_conexion(url, timeout):
        raise requests.ConnectionError("conexión rechazada")

    enviados = []
    monkeypatch.setattr(deploy.requests, "get", sin_conexion)
    registro = deploy.ejecutar_pipeline("http://staging/health", "s3cr3t", notificar=enviados.append)
    assert registro["resultado"] == deploy.ROLLBACK_CONEXION
    assert registro["http"] is None
    assert "SERVIDOR INACCESIBLE" in enviados[0]


@pytest.mark.parametrize("codigo, salida", [(200, 0), (500, 1)])
def test_main_codigo_de_salida(monkeypatch, codigo, salida):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setattr(deploy.requests, "get", lambda url, timeout: _Respuesta(codigo))
    assert deploy.main() == salida


# --- Telemetría a Telegram ---
def test_telegram_sin_configurar_se_omite(monkeypatch):
    def no_debe_llamarse(*args, **kwargs):
        raise AssertionError("no debe enviar sin credenciales")

    monkeypatch.setattr(deploy.requests, "post", no_debe_llamarse)
    assert deploy.notificar_telegram("hola", token="", chat_id="") is False


def test_telegram_envia_payload_correcto(monkeypatch):
    llamadas = []

    def falso_post(url, json, timeout):
        llamadas.append((url, json))
        return _Respuesta(200)

    monkeypatch.setattr(deploy.requests, "post", falso_post)
    assert deploy.notificar_telegram("hola", token="123:ABC", chat_id="999") is True
    url, payload = llamadas[0]
    assert url == "https://api.telegram.org/bot123:ABC/sendMessage"
    assert payload == {"chat_id": "999", "text": "hola", "parse_mode": "Markdown"}


def test_telegram_rechaza_devuelve_false(monkeypatch):
    monkeypatch.setattr(deploy.requests, "post", lambda url, json, timeout: _Respuesta(401))
    assert deploy.notificar_telegram("hola", token="malo", chat_id="999") is False


def test_telegram_error_de_red_no_filtra_el_token(monkeypatch, capsys):
    def falla(url, json, timeout):
        raise requests.ConnectionError(f"fallo al conectar con {url}")

    monkeypatch.setattr(deploy.requests, "post", falla)
    assert deploy.notificar_telegram("hola", token="123:TOKENSECRETO", chat_id="999") is False
    assert "TOKENSECRETO" not in capsys.readouterr().out


# --- Gate de reglas de negocio (caso de uso Banca) ---
def test_gate_de_reglas_fallido_bloquea_sin_tocar_staging(monkeypatch):
    def staging_no_debe_consultarse(url, timeout):
        raise AssertionError("con el gate fallido no se debe llegar a Staging")

    enviados = []
    monkeypatch.setattr(deploy.requests, "get", staging_no_debe_consultarse)
    registro = deploy.ejecutar_pipeline(
        "http://staging/health", "s3cr3t", notificar=enviados.append,
        gate_reglas=lambda: (False, "1 prueba(s) de reglas de crédito fallaron (casos B08)"),
    )
    assert registro["resultado"] == deploy.BLOQUEADO_REGLAS
    assert registro["gate_reglas"] == "fallido"
    assert "B08" in enviados[0] and "BLOQUEADO" in enviados[0]


def test_gate_de_reglas_aprobado_continua_al_smoke_test(monkeypatch):
    monkeypatch.setattr(deploy.requests, "get", lambda url, timeout: _Respuesta(200))
    registro = deploy.ejecutar_pipeline(
        "http://staging/health", "s3cr3t", notificar=lambda m: False,
        gate_reglas=lambda: (True, "28 de 28 pruebas de reglas de crédito aprobadas"),
    )
    assert registro["gate_reglas"] == "aprobado"
    assert registro["resultado"] == deploy.PROMOCIONADO
