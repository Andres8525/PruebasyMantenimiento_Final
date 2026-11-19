"""Semana 3 — Cobertura de Código y Quality Gates.

Componente del sistema de crédito: perfil del cliente.
Tiene 5 caminos lógicos (branches) que la suite debe cubrir al 100%.
"""


def evaluar_cliente(edad: int, es_preferencial: bool, cuenta_activa: bool) -> str:
    if not cuenta_activa:
        return "RECHAZADO_CUENTA_INACTIVA"

    if edad < 18:
        if es_preferencial:
            return "REQUIERE_CODEUDOR"
        return "RECHAZADO_MENOR_DE_EDAD"

    if es_preferencial:
        return "CREDITO_PREFERENCIAL"

    return "CREDITO_ESTANDAR"
