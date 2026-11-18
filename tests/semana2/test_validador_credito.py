"""Semana 2 — Suite parametrizada (BVA + DRY) del crédito bancario."""

import pytest

from src.semana2.validador_credito import evaluar_prestamo


@pytest.mark.parametrize(
    "score, ingresos, resultado_esperado",
    [
        # --- FRONTERAS DEL SCORE (ingresos fijos válidos de 2500.0) ---
        (599, 2500.0, "RECHAZADO"),  # Off Point: justo abajo del límite
        (600, 2500.0, "APROBADO"),   # On Point: límite exacto inferior
        (850, 2500.0, "APROBADO"),   # On Point: límite superior máximo
        # --- FRONTERAS DE LOS INGRESOS (score fijo válido de 700) ---
        (700, 1999.99, "RECHAZADO"),  # Off Point: 1 centavo abajo
        (700, 2000.00, "APROBADO"),   # On Point: ingreso mínimo exacto
    ],
)
def test_evaluar_prestamo_fronteras(score, ingresos, resultado_esperado):
    assert evaluar_prestamo(score, ingresos) == resultado_esperado


@pytest.mark.parametrize(
    "score_invalido, ingresos_invalidos, excepcion_esperada",
    [
        (299, 3000.0, ValueError),     # Score bajo el mínimo (300)
        (851, 3000.0, ValueError),     # Score sobre el máximo (850)
        (700, -50.0, ValueError),      # Ingreso negativo
        ("700", 2500.0, TypeError),    # Tipo string en score
        (700, None, TypeError),        # Nulo en ingresos
    ],
)
def test_evaluar_prestamo_excepciones(score_invalido, ingresos_invalidos, excepcion_esperada):
    with pytest.raises(excepcion_esperada):
        evaluar_prestamo(score_invalido, ingresos_invalidos)
