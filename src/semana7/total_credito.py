"""Semana 7 — Análisis Estático y Quality Gates (SonarCloud + linters).

Componente del sistema de crédito: total a pagar por el crédito.

Versión refactorizada. La versión "sucia" tenía una variable sin uso, la clave
del core bancario escrita en texto plano y un if/else con ramas idénticas;
SonarCloud la bloqueaba y esta es la corrección que la deja en verde.
"""


def calcular_total_credito(monto, tasa_interes):
    # Sin variables muertas, sin secretos y sin bifurcaciones redundantes.
    return monto + (monto * tasa_interes)
