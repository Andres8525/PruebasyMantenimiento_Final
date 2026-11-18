"""Semana 1 — Patrón AAA y Pytest.

Código de negocio entregado por el equipo de desarrollo para auditar.
Regla: un usuario de 18 años o más puede entrar.
"""


def verificar_acceso(edad):
    # Si el usuario tiene 18 años o más, puede entrar
    if edad >= 18:
        return "Permitido"
    else:
        return "Denegado"
