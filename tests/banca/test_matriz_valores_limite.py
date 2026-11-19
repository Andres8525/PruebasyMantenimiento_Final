"""Caso de uso: Banca — matriz de valores límite de la política de crédito.

Estas pruebas son el Gate de reglas de negocio: el pipeline de CD las ejecuta
antes de tocar Staging. Si un borde se mueve, el despliegue se bloquea.
"""

import pytest

from src.banca import politica

CASOS = politica.MATRIZ_BVA


@pytest.mark.parametrize("caso", CASOS, ids=[c["id"] for c in CASOS])
def test_matriz_valores_limite(caso):
    if caso["esperado"] == politica.ERROR:
        with pytest.raises((TypeError, ValueError)):
            politica.evaluar_solicitud(caso["score"], caso["ingresos"])
    else:
        resultado = politica.evaluar_solicitud(caso["score"], caso["ingresos"])
        assert resultado["decision"] == caso["esperado"]


def test_matriz_cubre_on_y_off_point_de_cada_regla():
    for regla in ("Score mínimo de aprobación", "Ingreso mínimo"):
        tipos = {c["tipo"] for c in CASOS if c["regla"] == regla}
        assert {"On point", "Off point"} <= tipos, regla


def test_ids_de_la_matriz_son_unicos():
    ids = [c["id"] for c in CASOS]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize(
    "score, ingresos, motivo_esperado",
    [
        (599, 2500.0, "Score 599 por debajo del mínimo de 600."),
        (700, 1999.99, "Ingresos 1,999.99 por debajo del mínimo de 2,000.00."),
        (700, 2000.0, "Cumple el score mínimo y el ingreso mínimo."),
    ],
)
def test_motivos_explican_la_decision(score, ingresos, motivo_esperado):
    assert motivo_esperado in politica.evaluar_solicitud(score, ingresos)["motivos"]


def test_rechazo_doble_lista_ambos_motivos():
    resultado = politica.evaluar_solicitud(599, 1999.99)
    assert resultado["decision"] == politica.RECHAZADO
    assert len(resultado["motivos"]) == 2


def test_politica_vigente_publica_los_bordes():
    vigente = politica.politica_vigente()
    assert vigente["score_minimo_aprobacion"] == 600
    assert vigente["ingreso_minimo"] == 2000.0
    assert vigente["score_dominio"] == [300, 850]
