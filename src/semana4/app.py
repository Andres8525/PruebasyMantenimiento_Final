"""Semana 4 — Cultura DevOps y Docker.

Lógica de negocio que se empaqueta junto con sus pruebas en un contenedor
inmutable (qa-runner). Calcula el descuento en certificación DevOps según la
cobertura de código obtenida.
"""


def evaluar_descuento_devops(cobertura_codigo: float, es_estudiante: bool) -> float:
    if cobertura_codigo < 0.0 or cobertura_codigo > 100.0:
        raise ValueError("La cobertura debe estar entre 0 y 100")

    if es_estudiante and cobertura_codigo >= 80.0:
        return 50.0  # 50% de descuento
    elif cobertura_codigo >= 90.0:
        return 30.0  # 30% de descuento

    return 0.0
