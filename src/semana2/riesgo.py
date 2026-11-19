"""Semana 2 — Reto en clase: clasificación por rangos con valores límite.

Componente del sistema de crédito: nivel de riesgo según el score crediticio.
Define la tasa de interés base de la solicitud.

    300 a 579  -> "ALTO"
    580 a 699  -> "MEDIO"
    700 a 850  -> "BAJO"
    < 300 o > 850 -> ValueError
"""

SCORE_MINIMO = 300
SCORE_MAXIMO = 850
LIMITE_RIESGO_MEDIO = 580
LIMITE_RIESGO_BAJO = 700


def clasificar_riesgo(score) -> str:
    if isinstance(score, bool) or not isinstance(score, int):
        raise TypeError("El score debe ser un número entero.")
    if score < SCORE_MINIMO or score > SCORE_MAXIMO:
        raise ValueError("El score debe estar entre 300 y 850.")

    if score < LIMITE_RIESGO_MEDIO:
        return "ALTO"
    if score < LIMITE_RIESGO_BAJO:
        return "MEDIO"
    return "BAJO"
