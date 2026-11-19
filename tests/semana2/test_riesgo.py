"""Semana 2 — Reto en clase: matriz BVA mínima de 8 casos límite para el nivel de riesgo."""

import pytest

from src.semana2.riesgo import clasificar_riesgo


@pytest.mark.parametrize(
    "score, resultado_esperado",
    [
        (300, "ALTO"),   # Límite inferior válido
        (579, "ALTO"),   # Borde superior de riesgo alto
        (580, "MEDIO"),  # Borde inferior de riesgo medio
        (699, "MEDIO"),  # Borde superior de riesgo medio
        (700, "BAJO"),   # Borde inferior de riesgo bajo
        (850, "BAJO"),   # Límite superior válido
    ],
)
def test_clasificar_riesgo_fronteras(score, resultado_esperado):
    assert clasificar_riesgo(score) == resultado_esperado


@pytest.mark.parametrize(
    "score_invalido, excepcion_esperada",
    [
        (299, ValueError),    # Límite inferior inválido
        (851, ValueError),    # Límite superior inválido
        ("700", TypeError),   # Tipo incorrecto
    ],
)
def test_clasificar_riesgo_invalido(score_invalido, excepcion_esperada):
    with pytest.raises(excepcion_esperada):
        clasificar_riesgo(score_invalido)
