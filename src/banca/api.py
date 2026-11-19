"""Caso de uso: Banca — API del servicio de evaluación de crédito.

Endpoints:
    GET  /health                       -> estado del servicio
    GET  /api/v1/creditos/politica     -> política de aprobación vigente
    POST /api/v1/creditos/evaluar      -> regla de aprobación (score e ingresos) con motivos
    POST /api/v1/creditos/solicitudes  -> solicitud completa: recorre los componentes de las semanas 1 a 7

El dashboard la monta en /banca para el simulador.
Ejecutar sola: python -m uvicorn src.banca.api:app --port 8002
"""

from typing import Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, StrictBool, StrictFloat, StrictInt

from src.banca import politica
from src.banca.solicitud import evaluar_solicitud_completa

app = FastAPI(title="servicio-credito", version=politica.VERSION_POLITICA)


Numero = Union[StrictFloat, StrictInt]


class Solicitud(BaseModel):
    score: StrictInt
    ingresos: Numero


class SolicitudCompleta(BaseModel):
    edad: StrictInt
    score: StrictInt
    ingresos: Numero
    monto: Numero
    cuenta_activa: StrictBool
    es_preferencial: StrictBool
    puntualidad: Numero
    es_cliente_nomina: StrictBool


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


@app.post("/api/v1/creditos/solicitudes")
def evaluar_solicitud(solicitud: SolicitudCompleta):
    datos = {campo: getattr(solicitud, campo) for campo in (
        "edad", "score", "ingresos", "monto", "cuenta_activa", "es_preferencial", "puntualidad", "es_cliente_nomina")}
    for campo in ("ingresos", "monto", "puntualidad"):
        datos[campo] = float(datos[campo])
    try:
        return evaluar_solicitud_completa(datos)
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
