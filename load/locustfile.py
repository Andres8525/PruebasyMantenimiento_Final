"""Semana 8 — Enjambre de usuarios para Locust.

Pesos: @task(3) a /fast y @task(1) a /slow -> 75% / 25% de las peticiones.

Modo interfaz:  python -m locust -f load/locustfile.py --host http://localhost:8000
Modo headless:  python scripts/run_load_test.py
"""

from locust import HttpUser, between, task


class WebsiteTestUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def test_fast(self):
        self.client.get("/fast")

    @task(1)
    def test_slow(self):
        self.client.get("/slow")
