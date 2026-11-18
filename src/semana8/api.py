"""Semana 8 — API "dummy" objetivo de las pruebas de carga con Locust.

/fast responde de inmediato; /slow simula un cuello de botella (p. ej. una
consulta lenta a base de datos) con una pausa de medio segundo.
"""

import time

from fastapi import FastAPI

app = FastAPI(title="load-target")

RETARDO_SLOW_SEGUNDOS = 0.5


@app.get("/fast")
def fast_endpoint():
    return {"status": "ok", "speed": "fast"}


@app.get("/slow")
def slow_endpoint():
    time.sleep(RETARDO_SLOW_SEGUNDOS)  # Emula un cuello de botella o base de datos lenta
    return {"status": "ok", "speed": "slow"}
