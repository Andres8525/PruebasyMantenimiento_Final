"""Semana 3 — Suite que recorre las 5 ramas lógicas (100% de cobertura)."""

import pytest

from src.semana3.validator import evaluar_acceso_usuario


@pytest.mark.parametrize(
    "edad, es_premium, esta_activo, resultado_esperado",
    [
        (25, False, False, "ACCESO_DENEGADO_INACTIVO"),  # Rama 1: inactivo
        (16, True, True, "ACCESO_MENOR_PREMIUM"),        # Rama 2: menor + premium
        (16, False, True, "ACCESO_DENEGADO_MENOR"),      # Rama 3: menor + no premium
        (20, True, True, "ACCESO_TOTAL_PREMIUM"),        # Rama 4: adulto + premium
        (20, False, True, "ACCESO_ESTANDAR"),            # Rama 5: adulto estándar
    ],
)
def test_evaluar_acceso_cobertura_total(edad, es_premium, esta_activo, resultado_esperado):
    resultado = evaluar_acceso_usuario(edad, es_premium, esta_activo)
    assert resultado == resultado_esperado
