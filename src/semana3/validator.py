"""Semana 3 — Cobertura de Código y Quality Gates.

Valida el nivel de acceso de un usuario según su estado, edad y membresía.
Tiene 5 caminos lógicos (branches) que la suite debe cubrir al 100%.
"""


def evaluar_acceso_usuario(edad: int, es_premium: bool, esta_activo: bool) -> str:
    if not esta_activo:
        return "ACCESO_DENEGADO_INACTIVO"

    if edad < 18:
        if es_premium:
            return "ACCESO_MENOR_PREMIUM"
        return "ACCESO_DENEGADO_MENOR"

    if es_premium:
        return "ACCESO_TOTAL_PREMIUM"

    return "ACCESO_ESTANDAR"
