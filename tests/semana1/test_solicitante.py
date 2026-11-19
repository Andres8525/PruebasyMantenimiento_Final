"""Semana 1 — Pruebas unitarias con el Patrón AAA (Arrange, Act, Assert).

Sistema de crédito: el solicitante debe ser mayor de edad.
"""

from src.semana1.solicitante import verificar_solicitante


def test_solicitante_menor_de_edad():
    # 1. Arrange
    edad_solicitante = 15
    # 2. Act
    resultado = verificar_solicitante(edad_solicitante)
    # 3. Assert
    assert resultado == "Denegado"


def test_solicitante_exactamente_18():
    # 1. Arrange — valor límite crítico
    edad_solicitante = 18
    # 2. Act
    resultado = verificar_solicitante(edad_solicitante)
    # 3. Assert
    assert resultado == "Permitido"


def test_solicitante_mayor_de_edad():
    # 1. Arrange — reto de clase
    edad_solicitante = 25
    # 2. Act
    resultado = verificar_solicitante(edad_solicitante)
    # 3. Assert
    assert resultado == "Permitido"


def test_solicitante_justo_debajo_del_limite():
    # 1. Arrange — "valor justo por debajo" del borde (17)
    edad_solicitante = 17
    # 2. Act
    resultado = verificar_solicitante(edad_solicitante)
    # 3. Assert
    assert resultado == "Denegado"
