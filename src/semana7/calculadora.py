"""Semana 7 — Análisis Estático y Quality Gates (SonarCloud + linters).

Versión refactorizada de calculadora.py. La versión "sucia" del laboratorio tenía
una variable sin uso, una contraseña en texto plano y un if/else con ramas
idénticas; SonarCloud la bloqueaba y esta es la corrección que la deja en verde.
"""


def calcular_total(precio, impuesto):
    # Sin variables muertas, sin secretos y sin bifurcaciones redundantes.
    return precio + (precio * impuesto)
