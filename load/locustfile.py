"""Semana 8 — Enjambre de clientes del banco para Locust.

Pesos: @task(3) a la simulación y @task(1) a la consulta al buró -> 75% / 25%.

Modo interfaz:  python -m locust -f load/locustfile.py --host http://localhost:8000
Modo headless:  python scripts/run_load_test.py
"""

from locust import HttpUser, between, task


class ClienteBanco(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def simular_credito(self):
        self.client.get("/api/v1/creditos/simulacion")

    @task(1)
    def consultar_buro(self):
        self.client.get("/api/v1/creditos/buro")
