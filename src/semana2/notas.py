"""Semana 2 — Reto en clase: evaluar_nota_estudiante(nota).

    0.0 a 2.9  -> "REPROBADO"
    3.0 a 4.5  -> "APROBADO"
    4.6 a 5.0  -> "EXCELENTE"
    < 0.0 o > 5.0 -> ValueError
"""


def evaluar_nota_estudiante(nota) -> str:
    if isinstance(nota, bool) or not isinstance(nota, (int, float)):
        raise TypeError("La nota debe ser un valor numérico.")
    if nota < 0.0 or nota > 5.0:
        raise ValueError("La nota debe estar entre 0.0 y 5.0.")

    if nota < 3.0:
        return "REPROBADO"
    if nota <= 4.5:
        return "APROBADO"
    return "EXCELENTE"
