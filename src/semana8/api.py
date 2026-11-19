"""Semana 8 — API objetivo de las pruebas de carga con Locust.

Componente del sistema de crédito: consultas masivas de los clientes.
    /api/v1/creditos/simulacion  responde de inmediato (cálculo local).
    /api/v1/creditos/buro        simula la consulta a la central de riesgo
                                 externa: el cuello de botella (0.5 s).
"""

import time

from fastapi import FastAPI

app = FastAPI(title="credito-carga")

RETARDO_BURO_SEGUNDOS = 0.5


@app.get("/api/v1/creditos/simulacion")
def simulacion():
    return {"status": "ok", "consulta": "simulacion"}


@app.get("/api/v1/creditos/buro")
def consulta_buro():
    time.sleep(RETARDO_BURO_SEGUNDOS)  # Emula la central de riesgo externa (cuello de botella)
    return {"status": "ok", "consulta": "buro"}
