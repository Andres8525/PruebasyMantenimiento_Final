"""Caso de uso: Banca — API del servicio de evaluación de crédito.

Endpoints:
    GET  /health                       -> estado del servicio
    GET  /api/v1/creditos/politica     -> política de aprobación vigente
    POST /api/v1/creditos/evaluar      -> decisión (APROBADO / RECHAZADO) con motivos

El dashboard la monta en /banca para el simulador.
Ejecutar sola: python -m uvicorn src.banca.api:app --port 8002
"""

from typing import Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, StrictFloat, StrictInt

from src.banca import politica

app = FastAPI(title="servicio-credito", version=politica.VERSION_POLITICA)


class Solicitud(BaseModel):
    score: StrictInt
    ingresos: Union[StrictFloat, StrictInt]


@app.get("/health")
def health():
    return {"status": "ok", "service": "servicio-credito", "politica": politica.VERSION_POLITICA}


@app.get("/api/v1/creditos/politica")
def obtener_politica():
    return politica.politica_vigente()


@app.post("/api/v1/creditos/evaluar")
def evaluar(solicitud: Solicitud):
    try:
        return politica.evaluar_solicitud(solicitud.score, float(solicitud.ingresos))
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
