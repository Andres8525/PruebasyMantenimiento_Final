"""Semana 2 — Partición de Equivalencia (EP) y Valores Límite (BVA).

Sistema de descuentos: solo aplica para edades entre 18 y 65 años (inclusive).
Entradas destructivas (negativos, texto, None, booleanos) lanzan ValueError.
"""

EDAD_MINIMA = 18
EDAD_MAXIMA = 65


def evaluar_edad(edad) -> str:
    # Validación defensiva: bool es subclase de int, por eso se descarta aparte
    if isinstance(edad, bool) or not isinstance(edad, int):
        raise ValueError("La edad debe ser un número entero.")
    if edad < 0:
        raise ValueError("La edad no puede ser negativa.")

    if EDAD_MINIMA <= edad <= EDAD_MAXIMA:
        return "Permitido"
    return "Denegado"
