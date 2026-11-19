"""Semana 2 — Partición de Equivalencia (EP) y Valores Límite (BVA).

Componente del sistema de crédito: rango de edad financiable.
El banco solo otorga créditos a solicitantes entre 18 y 65 años (inclusive),
porque el plazo de pago debe terminar antes de la edad máxima asegurable.
Entradas destructivas (negativos, texto, None, booleanos) lanzan ValueError.
"""

EDAD_MINIMA = 18
EDAD_MAXIMA = 65


def evaluar_edad_credito(edad) -> str:
    # Validación defensiva: bool es subclase de int, por eso se descarta aparte
    if isinstance(edad, bool) or not isinstance(edad, int):
        raise ValueError("La edad debe ser un número entero.")
    if edad < 0:
        raise ValueError("La edad no puede ser negativa.")

    if EDAD_MINIMA <= edad <= EDAD_MAXIMA:
        return "Permitido"
    return "Denegado"
