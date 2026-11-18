"""Semana 4 — Suite que corre dentro del contenedor qa-runner (exit code 0 = listo para CI/CD)."""

import pytest

from src.semana4.app import evaluar_descuento_devops


# --- Las 4 pruebas del laboratorio ---
def test_descuento_estudiante_alta_cobertura():
    assert evaluar_descuento_devops(85.0, True) == 50.0


def test_descuento_profesional_excelente_cobertura():
    assert evaluar_descuento_devops(95.0, False) == 30.0


def test_sin_descuento_baja_cobertura():
    assert evaluar_descuento_devops(70.0, False) == 0.0


def test_excepcion_cobertura_invalida():
    with pytest.raises(ValueError):
        evaluar_descuento_devops(150.0, True)


# --- Extensión: valores límite de cada regla (técnica de la Semana 2) ---
@pytest.mark.parametrize(
    "cobertura, es_estudiante, esperado",
    [
        (80.0, True, 50.0),    # On point estudiante
        (79.9, True, 0.0),     # Off point estudiante
        (90.0, False, 30.0),   # On point profesional
        (89.9, False, 0.0),    # Off point profesional
        (85.0, False, 0.0),    # Profesional con cobertura de estudiante
        (0.0, True, 0.0),      # Límite inferior válido
        (100.0, False, 30.0),  # Límite superior válido
    ],
)
def test_descuento_valores_limite(cobertura, es_estudiante, esperado):
    assert evaluar_descuento_devops(cobertura, es_estudiante) == esperado


@pytest.mark.parametrize("cobertura_invalida", [-0.1, 100.1])
def test_descuento_fuera_de_rango(cobertura_invalida):
    with pytest.raises(ValueError):
        evaluar_descuento_devops(cobertura_invalida, False)
