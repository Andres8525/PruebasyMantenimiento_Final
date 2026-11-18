"""Semana 6 — Integración Continua con GitHub Actions.

API base del "Kit de Rescate": el pipeline de CI la construye y la prueba
automáticamente en cada push o pull request hacia main.
"""

from fastapi import FastAPI

app = FastAPI(title="ci-api")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "API funcionando"}
