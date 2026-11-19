"""Semana 6 — Integración Continua con GitHub Actions.

Componente del sistema de crédito: servicio base. El pipeline de CI lo
construye y lo prueba automáticamente en cada push o pull request hacia main.
"""

from fastapi import FastAPI

app = FastAPI(title="servicio-credito-base")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Servicio de crédito funcionando"}
