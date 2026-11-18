"""Semana 2 — Reto en clase: matriz BVA mínima de 8 casos límite para notas."""

import pytest

from src.semana2.notas import evaluar_nota_estudiante


@pytest.mark.parametrize(
    "nota, resultado_esperado",
    [
        (0.0, "REPROBADO"),  # Límite inferior válido
        (2.9, "REPROBADO"),  # Borde superior de Reprobado
        (3.0, "APROBADO"),   # Borde inferior de Aprobado
        (4.5, "APROBADO"),   # Borde superior de Aprobado
        (4.6, "EXCELENTE"),  # Borde inferior de Excelente
        (5.0, "EXCELENTE"),  # Límite superior válido
    ],
)
def test_evaluar_nota_fronteras(nota, resultado_esperado):
    assert evaluar_nota_estudiante(nota) == resultado_esperado


@pytest.mark.parametrize(
    "nota_invalida, excepcion_esperada",
    [
        (-0.1, ValueError),   # Límite inferior inválido
        (5.1, ValueError),    # Límite superior inválido
        ("4.0", TypeError),   # Tipo incorrecto
    ],
)
def test_evaluar_nota_invalida(nota_invalida, excepcion_esperada):
    with pytest.raises(excepcion_esperada):
        evaluar_nota_estudiante(nota_invalida)
