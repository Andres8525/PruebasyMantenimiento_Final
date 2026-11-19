"""Caso de uso: Banca — política de aprobación de crédito.

La decisión la toma el validador de la Semana 2 (src/semana2/validador_credito.py).
Este módulo publica la política vigente, explica cada decisión con sus motivos y
define la MATRIZ DE VALORES LÍMITE que protege la regla.

Garantía del caso de uso: ningún cambio en las reglas de aprobación llega a
Producción sin pasar esta matriz. Si alguien mueve un borde en el validador
(por ejemplo, ingresos >= 2000 pasa a ingresos > 2000), los casos On/Off point
fallan, el Quality Gate se rechaza y el pipeline de CD bloquea el despliegue.
"""

from __future__ import annotations

from src.semana2.validador_credito import evaluar_prestamo

VERSION_POLITICA = "2026.1"
SCORE_DOMINIO_MIN = 300
SCORE_DOMINIO_MAX = 850
SCORE_MINIMO_APROBACION = 600
INGRESO_MINIMO = 2000.00

APROBADO = "APROBADO"
RECHAZADO = "RECHAZADO"
ERROR = "ERROR"


def politica_vigente() -> dict:
    return {
        "version": VERSION_POLITICA,
        "score_dominio": [SCORE_DOMINIO_MIN, SCORE_DOMINIO_MAX],
        "score_minimo_aprobacion": SCORE_MINIMO_APROBACION,
        "ingreso_minimo": INGRESO_MINIMO,
        "regla": f"Se aprueba si el score está entre {SCORE_MINIMO_APROBACION} y {SCORE_DOMINIO_MAX} "
                 f"y los ingresos mensuales son de al menos {INGRESO_MINIMO:,.2f}.",
    }


def evaluar_solicitud(score, ingresos) -> dict:
    """Evalúa una solicitud y explica la decisión. Propaga TypeError/ValueError del validador."""
    decision = evaluar_prestamo(score, ingresos)
    motivos = []
    if score < SCORE_MINIMO_APROBACION:
        motivos.append(f"Score {score} por debajo del mínimo de {SCORE_MINIMO_APROBACION}.")
    if ingresos < INGRESO_MINIMO:
        motivos.append(f"Ingresos {ingresos:,.2f} por debajo del mínimo de {INGRESO_MINIMO:,.2f}.")
    if not motivos:
        motivos.append("Cumple el score mínimo y el ingreso mínimo.")
    return {
        "decision": decision,
        "motivos": motivos,
        "score": score,
        "ingresos": ingresos,
        "politica": VERSION_POLITICA,
    }


# Matriz de valores límite: cada borde de la regla se prueba exactamente en el
# límite (On point) y justo al lado (Off point), más los bordes del dominio.
MATRIZ_BVA = [
    {"id": "B01", "regla": "Dominio del score", "tipo": "Fuera de dominio",
     "score": SCORE_DOMINIO_MIN - 1, "ingresos": 3000.0, "esperado": ERROR},
    {"id": "B02", "regla": "Dominio del score", "tipo": "Límite inferior válido",
     "score": SCORE_DOMINIO_MIN, "ingresos": 3000.0, "esperado": RECHAZADO},
    {"id": "B03", "regla": "Score mínimo de aprobación", "tipo": "Off point",
     "score": SCORE_MINIMO_APROBACION - 1, "ingresos": 2500.0, "esperado": RECHAZADO},
    {"id": "B04", "regla": "Score mínimo de aprobación", "tipo": "On point",
     "score": SCORE_MINIMO_APROBACION, "ingresos": 2500.0, "esperado": APROBADO},
    {"id": "B05", "regla": "Dominio del score", "tipo": "Límite superior válido",
     "score": SCORE_DOMINIO_MAX, "ingresos": 2500.0, "esperado": APROBADO},
    {"id": "B06", "regla": "Dominio del score", "tipo": "Fuera de dominio",
     "score": SCORE_DOMINIO_MAX + 1, "ingresos": 3000.0, "esperado": ERROR},
    {"id": "B07", "regla": "Ingreso mínimo", "tipo": "Off point",
     "score": 700, "ingresos": round(INGRESO_MINIMO - 0.01, 2), "esperado": RECHAZADO},
    {"id": "B08", "regla": "Ingreso mínimo", "tipo": "On point",
     "score": 700, "ingresos": INGRESO_MINIMO, "esperado": APROBADO},
    {"id": "B09", "regla": "Dominio de ingresos", "tipo": "Límite inferior válido",
     "score": 700, "ingresos": 0.0, "esperado": RECHAZADO},
    {"id": "B10", "regla": "Dominio de ingresos", "tipo": "Fuera de dominio",
     "score": 700, "ingresos": -0.01, "esperado": ERROR},
    {"id": "B11", "regla": "Ambas reglas", "tipo": "Off point doble",
     "score": SCORE_MINIMO_APROBACION - 1, "ingresos": round(INGRESO_MINIMO - 0.01, 2), "esperado": RECHAZADO},
    {"id": "B12", "regla": "Tipo de dato", "tipo": "Entrada inválida",
     "score": "700", "ingresos": 2500.0, "esperado": ERROR},
]
