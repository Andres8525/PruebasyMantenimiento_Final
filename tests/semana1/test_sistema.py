"""Semana 1 — Pruebas unitarias con el Patrón AAA (Arrange, Act, Assert)."""

from src.semana1.sistema import verificar_acceso


def test_acceso_menor_de_edad():
    # 1. Arrange
    edad_usuario = 15
    # 2. Act
    resultado = verificar_acceso(edad_usuario)
    # 3. Assert
    assert resultado == "Denegado"


def test_acceso_exactamente_18():
    # 1. Arrange — valor límite crítico
    edad_usuario = 18
    # 2. Act
    resultado = verificar_acceso(edad_usuario)
    # 3. Assert
    assert resultado == "Permitido"


def test_acceso_mayor_de_edad():
    # 1. Arrange — reto de clase
    edad_usuario = 25
    # 2. Act
    resultado = verificar_acceso(edad_usuario)
    # 3. Assert
    assert resultado == "Permitido"


def test_acceso_justo_debajo_del_limite():
    # 1. Arrange — "valor justo por debajo" del borde (17)
    edad_usuario = 17
    # 2. Act
    resultado = verificar_acceso(edad_usuario)
    # 3. Assert
    assert resultado == "Denegado"
