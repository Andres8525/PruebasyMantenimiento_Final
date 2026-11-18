"""Semana 7 — Pruebas de la calculadora refactorizada.

Garantizan que la refactorización pedida por SonarCloud no cambió el resultado:
el cálculo es el mismo por encima y por debajo de 100 (las ramas eran idénticas).
"""

import pytest

from src.semana7.calculadora import calcular_total


@pytest.mark.parametrize(
    "precio, impuesto, esperado",
    [
        (100, 0.19, 119.0),   # Borde del antiguo if precio > 100
        (101, 0.19, 120.19),  # Justo por encima del antiguo borde
        (50, 0.19, 59.5),     # Rama del antiguo else
        (0, 0.19, 0.0),       # Precio cero
        (200, 0.0, 200.0),    # Sin impuesto
    ],
)
def test_calcular_total(precio, impuesto, esperado):
    assert calcular_total(precio, impuesto) == pytest.approx(esperado)
