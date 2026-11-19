"""Semana 1 — Patrón AAA y Pytest.

Componente del sistema de crédito: verificación del solicitante.
Regla: solo una persona de 18 años o más puede solicitar un crédito.
"""

EDAD_MINIMA_SOLICITANTE = 18


def verificar_solicitante(edad):
    # Si el solicitante tiene 18 años o más, puede solicitar el crédito
    if edad >= 18:
        return "Permitido"
    else:
        return "Denegado"
