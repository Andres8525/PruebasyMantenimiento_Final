"""Semana 7 — Pruebas del cálculo del total a pagar (versión refactorizada).

Garantizan que la refactorización pedida por SonarCloud no cambió el resultado.
"""

import pytest

from src.semana7.total_credito import calcular_total_credito


@pytest.mark.parametrize(
    "monto, tasa_interes, esperado",
    [
        (10000, 0.12, 11200.0),  # Riesgo bajo
        (10000, 0.18, 11800.0),  # Riesgo medio
        (5000, 0.25, 6250.0),    # Riesgo alto
        (0, 0.12, 0.0),          # Monto cero
        (8000, 0.0, 8000.0),     # Sin interés
    ],
)
def test_calcular_total_credito(monto, tasa_interes, esperado):
    assert calcular_total_credito(monto, tasa_interes) == pytest.approx(esperado)
