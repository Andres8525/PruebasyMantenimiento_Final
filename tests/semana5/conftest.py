"""Fixture de la URL de la API para las pruebas de la Semana 5.

- Si existe la variable de entorno API_URL (modo contenedor / CI), las pruebas
  golpean ese servicio real (p. ej. http://api-service:8000 en Docker Compose).
- Si no existe (modo local), se levanta la API con Uvicorn en un hilo en un
  puerto libre, para que la suite funcione sin Docker.
"""

import os
import socket
import threading
import time

import pytest
import requests
import uvicorn


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def base_url():
    url_externa = os.getenv("API_URL")
    if url_externa:
        yield url_externa.rstrip("/")
        return

    from src.semana5.main import app

    puerto = _puerto_libre()
    config = uvicorn.Config(app, host="127.0.0.1", port=puerto, log_level="warning", ws="none")
    server = uvicorn.Server(config)
    hilo = threading.Thread(target=server.run, daemon=True)
    hilo.start()

    url = f"http://127.0.0.1:{puerto}"
    limite = time.time() + 10
    while time.time() < limite:
        try:
            if requests.get(f"{url}/health", timeout=0.5).status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(0.1)
    else:
        pytest.fail("La API local no arrancó a tiempo")

    yield url

    server.should_exit = True
    hilo.join(timeout=5)
