"""Caso de uso: Banca — una solicitud de crédito completa recorre todos los componentes.

Cada escenario prueba la integración de las semanas 1 a 7 en una sola decisión.
"""

import pytest
from fastapi.testclient import TestClient

from src.banca.api import app
from src.banca.solicitud import SOLICITUD_EJEMPLO, evaluar_solicitud_completa

client = TestClient(app)


def solicitud(**cambios):
    return {**SOLICITUD_EJEMPLO, **cambios}


def test_cliente_ideal_aprobado_con_tasa_y_total():
    resultado = evaluar_solicitud_completa(solicitud())
    assert resultado["decision"] == "APROBADO"
    assert resultado["nivel_riesgo"] == "BAJO"         # Semana 2: score 720
    assert resultado["descuento_tasa"] == 50.0         # Semana 4: nómina + 95% puntual
    assert resultado["tasa_final"] == pytest.approx(0.06)
    assert resultado["total_a_pagar"] == pytest.approx(10600.0)  # Semana 7


def test_la_solicitud_pasa_por_todas_las_semanas():
    semanas = {p["semana"] for p in evaluar_solicitud_completa(solicitud())["pasos"]}
    assert semanas == {1, 2, 3, 4, 7}


def test_riesgo_medio_sin_nomina_aplica_descuento_por_historial():
    resultado = evaluar_solicitud_completa(solicitud(score=650, puntualidad=92.0, es_cliente_nomina=False))
    assert resultado["decision"] == "APROBADO"
    assert resultado["nivel_riesgo"] == "MEDIO"
    assert resultado["tasa_final"] == pytest.approx(0.126)
    assert resultado["total_a_pagar"] == pytest.approx(11260.0)


@pytest.mark.parametrize(
    "cambios, semana_que_rechaza",
    [
        ({"ingresos": 1999.99}, 2),            # borde de ingresos: un centavo
        ({"score": 599}, 2),                   # borde del score mínimo
        ({"edad": 66}, 2),                     # fuera del rango financiable
        ({"edad": 17}, 1),                     # menor de edad
        ({"cuenta_activa": False}, 3),         # perfil: cuenta inactiva
    ],
)
def test_rechazo_indica_el_componente_responsable(cambios, semana_que_rechaza):
    resultado = evaluar_solicitud_completa(solicitud(**cambios))
    assert resultado["decision"] == "RECHAZADO"
    assert resultado["total_a_pagar"] is None
    assert any(m.startswith(f"Semana {semana_que_rechaza} ") for m in resultado["motivos"])


@pytest.mark.parametrize("cambios", [{"monto": 0}, {"edad": -1}, {"score": 851}, {"puntualidad": 101.0}])
def test_datos_fuera_de_dominio_lanzan_error(cambios):
    with pytest.raises((TypeError, ValueError)):
        evaluar_solicitud_completa(solicitud(**cambios))


def test_api_solicitud_completa_aprobada():
    respuesta = client.post("/api/v1/creditos/solicitudes", json=solicitud())
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["decision"] == "APROBADO"
    assert len(cuerpo["pasos"]) == 7


@pytest.mark.parametrize(
    "cambios",
    [{"monto": 0}, {"edad": "30"}, {"cuenta_activa": "si"}, {"score": 900}],
)
def test_api_solicitud_invalida_devuelve_422(cambios):
    assert client.post("/api/v1/creditos/solicitudes", json=solicitud(**cambios)).status_code == 422
