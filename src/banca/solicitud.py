"""Caso de uso: Banca — evaluación de una solicitud de crédito completa.

Una sola solicitud recorre los componentes construidos semana a semana:

    Semana 1  verificar_solicitante      mayoría de edad
    Semana 2  evaluar_edad_credito       rango de edad financiable (18 a 65)
    Semana 2  clasificar_riesgo          nivel de riesgo por score -> tasa base
    Semana 2  evaluar_prestamo           regla de aprobación: score e ingresos
    Semana 3  evaluar_cliente            perfil del cliente (cuenta, preferencial)
    Semana 4  calcular_descuento_tasa    descuento por puntualidad y nómina
    Semana 7  calcular_total_credito     total a pagar

La solicitud se aprueba solo si todos los componentes la aceptan.
"""

from __future__ import annotations

from src.banca.politica import APROBADO, RECHAZADO, VERSION_POLITICA
from src.semana1.solicitante import verificar_solicitante
from src.semana2.edad_credito import evaluar_edad_credito
from src.semana2.riesgo import clasificar_riesgo
from src.semana2.validador_credito import evaluar_prestamo
from src.semana3.perfil_cliente import evaluar_cliente
from src.semana4.tasa_interes import calcular_descuento_tasa
from src.semana7.total_credito import calcular_total_credito

TASA_BASE = {"BAJO": 0.12, "MEDIO": 0.18, "ALTO": 0.25}
PERFILES_APROBABLES = {"CREDITO_PREFERENCIAL", "CREDITO_ESTANDAR"}

SOLICITUD_EJEMPLO = {
    "edad": 30, "score": 720, "ingresos": 3000.0, "monto": 10000.0,
    "cuenta_activa": True, "es_preferencial": False, "puntualidad": 95.0, "es_cliente_nomina": True,
}


def evaluar_solicitud_completa(solicitud: dict) -> dict:
    """Devuelve la decisión, los motivos y el veredicto de cada componente (por semana)."""
    s = solicitud
    if not isinstance(s["monto"], (int, float)) or isinstance(s["monto"], bool) or s["monto"] <= 0:
        raise ValueError("El monto solicitado debe ser un número mayor que cero.")

    pasos = []

    def paso(semana: int, componente: str, resultado: str, ok: bool) -> None:
        pasos.append({"semana": semana, "componente": componente, "resultado": resultado, "ok": ok})

    edad_credito = evaluar_edad_credito(s["edad"])  # valida el tipo antes de comparar
    solicitante = verificar_solicitante(s["edad"])
    paso(1, "Mayoría de edad del solicitante", solicitante, solicitante == "Permitido")
    paso(2, "Rango de edad financiable (18 a 65)", edad_credito, edad_credito == "Permitido")

    riesgo = clasificar_riesgo(s["score"])
    paso(2, "Nivel de riesgo por score", riesgo, True)

    regla = evaluar_prestamo(s["score"], s["ingresos"])
    paso(2, "Regla de aprobación: score e ingresos", regla, regla == APROBADO)

    perfil = evaluar_cliente(s["edad"], s["es_preferencial"], s["cuenta_activa"])
    paso(3, "Perfil del cliente", perfil, perfil in PERFILES_APROBABLES)

    descuento = calcular_descuento_tasa(s["puntualidad"], s["es_cliente_nomina"])
    paso(4, "Descuento sobre la tasa de interés", f"{descuento:.0f}%", True)

    aprobado = all(p["ok"] for p in pasos)
    tasa_final = round(TASA_BASE[riesgo] * (1 - descuento / 100), 4)
    total = round(calcular_total_credito(s["monto"], tasa_final), 2) if aprobado else None
    paso(7, "Total a pagar", f"{total:,.2f}" if aprobado else "No aplica", True)

    motivos = [f"Semana {p['semana']} - {p['componente']}: {p['resultado']}" for p in pasos if not p["ok"]]
    return {
        "decision": APROBADO if aprobado else RECHAZADO,
        "motivos": motivos or ["La solicitud cumple todas las reglas del banco."],
        "pasos": pasos,
        "nivel_riesgo": riesgo,
        "tasa_base": TASA_BASE[riesgo],
        "descuento_tasa": descuento,
        "tasa_final": tasa_final,
        "monto": s["monto"],
        "total_a_pagar": total,
        "politica": VERSION_POLITICA,
    }
