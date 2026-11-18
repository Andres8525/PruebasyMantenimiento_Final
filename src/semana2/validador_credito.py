"""Semana 2 — Caso de estudio: Sistema de Evaluación de Crédito Bancario.

Regla de negocio: aprobar si el score está entre 600 y 850 y los ingresos
mensuales son >= 2000. Ambas condiciones deben cumplirse simultáneamente.
"""


def evaluar_prestamo(score: int, ingresos: float) -> str:
    # 1. Validación de tipo estricta
    if not isinstance(score, int) or isinstance(score, bool):
        raise TypeError("El score debe ser un número entero.")
    if not isinstance(ingresos, (int, float)) or isinstance(ingresos, bool):
        raise TypeError("Los ingresos deben ser un valor numérico.")

    # 2. Validación de límites del dominio
    if score < 300 or score > 850:
        raise ValueError("Score fuera de rango financiero permitido (300-850).")
    if ingresos < 0:
        raise ValueError("Los ingresos no pueden ser negativos.")

    # 3. Lógica de negocio (BVA)
    if score >= 600 and ingresos >= 2000.0:
        return "APROBADO"

    return "RECHAZADO"
