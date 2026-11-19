"""Semana 2 — BVA + parametrización sobre el rango de edad financiable (18 a 65 años)."""

import pytest

from src.semana2.edad_credito import evaluar_edad_credito


@pytest.mark.parametrize(
    "edad, resultado_esperado",
    [
        (17, "Denegado"),   # BVA: justo abajo
        (18, "Permitido"),  # BVA: límite exacto inferior
        (65, "Permitido"),  # BVA: límite exacto superior
        (66, "Denegado"),   # BVA: justo arriba
    ],
)
def test_edad_credito_limites(edad, resultado_esperado):
    assert evaluar_edad_credito(edad) == resultado_esperado


@pytest.mark.parametrize(
    "edad, resultado_esperado",
    [
        (15, "Denegado"),   # EP: clase inválida menor
        (30, "Permitido"),  # EP: clase válida
        (70, "Denegado"),   # EP: clase inválida mayor
    ],
)
def test_edad_credito_particion_equivalencia(edad, resultado_esperado):
    assert evaluar_edad_credito(edad) == resultado_esperado


@pytest.mark.parametrize("entrada_invalida", [-1, -100, "dieciocho", None, True])
def test_edad_credito_entradas_invalidas(entrada_invalida):
    with pytest.raises(ValueError):
        evaluar_edad_credito(entrada_invalida)
