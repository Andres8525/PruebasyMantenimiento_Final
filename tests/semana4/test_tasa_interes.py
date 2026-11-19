"""Semana 4 — Suite que corre dentro del contenedor qa-runner (exit code 0 = listo para CI/CD).

Sistema de crédito: descuento sobre la tasa de interés.
"""

import pytest

from src.semana4.tasa_interes import calcular_descuento_tasa


# --- Las 4 pruebas del laboratorio ---
def test_descuento_cliente_nomina_puntual():
    assert calcular_descuento_tasa(85.0, True) == 50.0


def test_descuento_cliente_excelente_historial():
    assert calcular_descuento_tasa(95.0, False) == 30.0


def test_sin_descuento_historial_irregular():
    assert calcular_descuento_tasa(70.0, False) == 0.0


def test_excepcion_puntualidad_invalida():
    with pytest.raises(ValueError):
        calcular_descuento_tasa(150.0, True)


# --- Extensión: valores límite de cada regla (técnica de la Semana 2) ---
@pytest.mark.parametrize(
    "puntualidad, es_cliente_nomina, esperado",
    [
        (80.0, True, 50.0),    # On point cliente de nómina
        (79.9, True, 0.0),     # Off point cliente de nómina
        (90.0, False, 30.0),   # On point historial excelente
        (89.9, False, 0.0),    # Off point historial excelente
        (85.0, False, 0.0),    # Sin nómina con puntualidad de nómina
        (0.0, True, 0.0),      # Límite inferior válido
        (100.0, False, 30.0),  # Límite superior válido
    ],
)
def test_descuento_valores_limite(puntualidad, es_cliente_nomina, esperado):
    assert calcular_descuento_tasa(puntualidad, es_cliente_nomina) == esperado


@pytest.mark.parametrize("puntualidad_invalida", [-0.1, 100.1])
def test_descuento_fuera_de_rango(puntualidad_invalida):
    with pytest.raises(ValueError):
        calcular_descuento_tasa(puntualidad_invalida, False)
