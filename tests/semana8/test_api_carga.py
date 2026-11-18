"""Semana 8 — Pruebas funcionales del objetivo de carga.

La prueba de carga en sí la hace Locust (load/locustfile.py); aquí se valida que
los endpoints respondan bien y que el cuello de botella exista como se diseñó.
"""

import time

from fastapi.testclient import TestClient

from src.semana8.api import RETARDO_SLOW_SEGUNDOS, app

client = TestClient(app)


def test_fast_responde_ok():
    response = client.get("/fast")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "speed": "fast"}


def test_slow_responde_ok():
    response = client.get("/slow")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "speed": "slow"}


def test_slow_tiene_cuello_de_botella():
    inicio = time.perf_counter()
    client.get("/slow")
    assert time.perf_counter() - inicio >= RETARDO_SLOW_SEGUNDOS
