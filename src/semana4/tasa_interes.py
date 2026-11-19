"""Semana 4 — Cultura DevOps y Docker.

Componente del sistema de crédito: descuento sobre la tasa de interés.
Se empaqueta junto con sus pruebas en el contenedor inmutable qa-runner.

    puntualidad: porcentaje de cuotas pagadas a tiempo en el historial (0 a 100)
    es_cliente_nomina: el cliente recibe su salario en el banco
"""


def calcular_descuento_tasa(puntualidad: float, es_cliente_nomina: bool) -> float:
    if puntualidad < 0.0 or puntualidad > 100.0:
        raise ValueError("La puntualidad debe estar entre 0 y 100")

    if es_cliente_nomina and puntualidad >= 80.0:
        return 50.0  # 50% de descuento sobre la tasa
    elif puntualidad >= 90.0:
        return 30.0  # 30% de descuento sobre la tasa

    return 0.0
