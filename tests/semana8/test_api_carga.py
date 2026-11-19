"""Semana 8 — Pruebas funcionales del objetivo de carga del sistema de crédito.

La prueba de carga en sí la hace Locust (load/locustfile.py); aquí se valida que
los endpoints respondan bien y que el cuello de botella del buró exista.
"""

import time

from fastapi.testclient import TestClient

from src.semana8.api import RETARDO_BURO_SEGUNDOS, app

client = TestClient(app)


def test_simulacion_responde_ok():
    response = client.get("/api/v1/creditos/simulacion")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "consulta": "simulacion"}


def test_buro_responde_ok():
    response = client.get("/api/v1/creditos/buro")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "consulta": "buro"}


def test_buro_es_el_cuello_de_botella():
    inicio = time.perf_counter()
    client.get("/api/v1/creditos/buro")
    assert time.perf_counter() - inicio >= RETARDO_BURO_SEGUNDOS
