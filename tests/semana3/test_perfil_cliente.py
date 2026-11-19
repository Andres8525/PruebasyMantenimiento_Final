"""Semana 3 — Suite que recorre las 5 ramas lógicas del perfil del cliente (100% de cobertura)."""

import pytest

from src.semana3.perfil_cliente import evaluar_cliente


@pytest.mark.parametrize(
    "edad, es_preferencial, cuenta_activa, resultado_esperado",
    [
        (25, False, False, "RECHAZADO_CUENTA_INACTIVA"),  # Rama 1: cuenta inactiva
        (16, True, True, "REQUIERE_CODEUDOR"),            # Rama 2: menor + preferencial
        (16, False, True, "RECHAZADO_MENOR_DE_EDAD"),     # Rama 3: menor + estándar
        (20, True, True, "CREDITO_PREFERENCIAL"),         # Rama 4: adulto + preferencial
        (20, False, True, "CREDITO_ESTANDAR"),            # Rama 5: adulto estándar
    ],
)
def test_evaluar_cliente_cobertura_total(edad, es_preferencial, cuenta_activa, resultado_esperado):
    resultado = evaluar_cliente(edad, es_preferencial, cuenta_activa)
    assert resultado == resultado_esperado
