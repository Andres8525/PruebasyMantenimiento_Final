"""Semana 9 — API objetivo del pipeline de Despliegue Continuo (CD).

El endpoint /health es el que audita el Smoke Test en Staging:
    IS_HEALTHY = True  -> HTTP 200 (Caso A: promoción a Producción)
    IS_HEALTHY = False -> HTTP 500 (Caso B: rollback automático)

Además de editar la constante, se puede arrancar con STAGING_HEALTHY=false
para simular el fallo sin tocar el código (así lo hace el pipeline).
"""

import os

from fastapi import FastAPI, Response, status

app = FastAPI(title="cd-api")

VERSION = "1.0.0"

# Control manual para simular salud en Staging/Producción
IS_HEALTHY = os.getenv("STAGING_HEALTHY", "true").strip().lower() != "false"


@app.get("/")
def root():
    return {"status": "online", "version": VERSION, "env": os.getenv("APP_ENV", "Production")}


@app.get("/health")
def health_check(response: Response):
    if not IS_HEALTHY:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "unhealthy", "reason": "Fallo detectado en Staging"}
    return {"status": "healthy", "version": VERSION}
