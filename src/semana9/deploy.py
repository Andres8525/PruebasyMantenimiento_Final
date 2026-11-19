"""Semana 9 — Motor del pipeline de CD: Smoke Test en Staging, promoción o
rollback automático, y telemetría a Telegram.

Uso:
    python -m src.semana9.deploy

Variables de entorno (NUNCA en el código; en CI vienen de GitHub Secrets):
    STAGING_HEALTH_URL   URL del /health de Staging (por defecto http://localhost:8001/health)
    API_SECRET_KEY       Secreto de la aplicación (se muestra enmascarado: abc***)
    TELEGRAM_BOT_TOKEN   Token del bot creado con @BotFather
    TELEGRAM_CHAT_ID     ID numérico del chat (obtenido con @userinfobot)

Si faltan las variables de Telegram el pipeline funciona igual y solo omite la alerta.
Código de salida: 0 = promocionado a Producción, 1 = rollback.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime

import requests

VERSION_ESTABLE = "1.0.0"
STAGING_HEALTH_URL_DEFECTO = "http://localhost:8001/health"
SECRETO_DEFECTO = "default_secret_dev"
TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"

PROMOCIONADO = "PROMOCIONADO"
ROLLBACK = "ROLLBACK"
ROLLBACK_CONEXION = "ROLLBACK_CONEXION"
BLOQUEADO_REGLAS = "BLOQUEADO_REGLAS"

MSG_EXITO = (
    "🚀 *DESPLIEGUE EXITOSO EN PRODUCCIÓN*\n\n"
    "• *Servicio:* API Principal (FastAPI)\n"
    "• *Entorno:* Producción\n"
    "• *Smoke Test:* 200 OK en Staging\n"
    f"• *Estado:* v{VERSION_ESTABLE} Operativa"
)
MSG_ROLLBACK = (
    "🚨 *ALERTA: ROLLBACK AUTOMÁTICO ACTIVADO*\n\n"
    "• *Servicio:* API Principal\n"
    "• *Fallo en Staging:* HTTP {codigo}\n"
    "• *Acción:* Despliegue abortado\n"
    f"• *Estado actual:* Se mantiene v{VERSION_ESTABLE} estable"
)
MSG_CAIDO = (
    "🚨 *ALERTA CRÍTICA: SERVIDOR INACCESIBLE*\n\n"
    "• *Acción:* Rollback ejecutado por Timeout/Conexión.\n"
    f"• *Estado actual:* Se mantiene v{VERSION_ESTABLE} estable"
)
MSG_REGLAS = (
    "🚨 *DESPLIEGUE BLOQUEADO: REGLAS DE CRÉDITO*\n\n"
    "• *Servicio:* Evaluación de crédito\n"
    "• *Motivo:* {detalle}\n"
    "• *Acción:* El cambio no llegó a Staging ni a Producción\n"
    f"• *Estado actual:* Se mantiene v{VERSION_ESTABLE} estable"
)


def enmascarar(secreto: str) -> str:
    """Muestra solo los 3 primeros caracteres: nunca se imprime un secreto completo."""
    return f"{secreto[:3]}***" if secreto else "(vacío)"


def notificar_telegram(mensaje: str, token: str | None = None, chat_id: str | None = None) -> bool:
    """Envía la alerta a Telegram con un POST estándar. Devuelve True si se entregó."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "") if token is None else token
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "") if chat_id is None else chat_id
    if not token or not chat_id:
        print("    (Telegram no configurado: se omite la notificación)")
        return False

    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try:
        respuesta = requests.post(TELEGRAM_API.format(token=token), json=payload, timeout=5)
    except requests.RequestException as error:
        # Solo el tipo de error: el mensaje completo incluye la URL, y la URL lleva el token.
        print(f"    No se pudo enviar la notificación: {type(error).__name__}")
        return False
    if respuesta.status_code != 200:
        print(f"    Telegram rechazó la notificación (HTTP {respuesta.status_code})")
        return False
    print("    Notificación enviada a Telegram")
    return True


def ejecutar_pipeline(url: str, secreto: str, notificar=notificar_telegram, gate_reglas=None) -> dict:
    """[Gate de reglas] -> Smoke Test en Staging -> promoción o rollback.

    gate_reglas: función opcional que devuelve (ok, detalle). Si falla, el despliegue
    se bloquea antes de tocar Staging (caso de uso Banca).
    """
    registro = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "url": url,
        "token": enmascarar(secreto),
        "http": None,
        "gate_reglas": None,
    }
    print("=== INICIANDO PIPELINE DE DESPLIEGUE CONTINUO (CD) ===")
    if gate_reglas is not None:
        print("[0/3] Gate de reglas de negocio: matriz de valores límite del crédito...")
        ok, detalle = gate_reglas()
        registro["gate_reglas"] = "aprobado" if ok else "fallido"
        if not ok:
            print(f" -> [BLOQUEADO] {detalle}")
            print(" El cambio en las reglas de aprobación no llega a Producción.")
            registro.update(resultado=BLOQUEADO_REGLAS, detalle=detalle)
            registro["telegram"] = notificar(MSG_REGLAS.format(detalle=detalle))
            return registro
        print(f" -> [OK] {detalle}")
    print(f"[1/3] Verificando credenciales inyectadas... Token: {registro['token']}")
    print(f"[2/3] Ejecutando Smoke Test en Staging ({url})...")
    try:
        respuesta = requests.get(url, timeout=3)
    except requests.RequestException as error:
        print(f" -> [ERROR DE CONEXIÓN]: {type(error).__name__}")
        print(" ACTIVANDO ROLLBACK AUTOMÁTICO: Restaurando versión previa.")
        registro.update(resultado=ROLLBACK_CONEXION, detalle="Staging inaccesible")
        registro["telegram"] = notificar(MSG_CAIDO)
        return registro

    registro["http"] = respuesta.status_code
    if respuesta.status_code == 200:
        print(" -> [OK] Health Check exitoso en Staging (HTTP 200).")
        print("[3/3] PROMOCIONANDO A PRODUCCIÓN: ¡Despliegue completado con éxito!")
        registro.update(resultado=PROMOCIONADO, detalle="Smoke Test 200 OK")
        registro["telegram"] = notificar(MSG_EXITO)
    else:
        print(f" -> [ERROR] Health Check falló con estatus {respuesta.status_code}.")
        print(f" ACTIVANDO ROLLBACK AUTOMÁTICO: Cancelando despliegue y manteniendo v{VERSION_ESTABLE} estable.")
        registro.update(resultado=ROLLBACK, detalle=f"Smoke Test HTTP {respuesta.status_code}")
        registro["telegram"] = notificar(MSG_ROLLBACK.format(codigo=respuesta.status_code))
    return registro


def main() -> int:
    url = os.getenv("STAGING_HEALTH_URL") or STAGING_HEALTH_URL_DEFECTO
    secreto = os.getenv("API_SECRET_KEY") or SECRETO_DEFECTO
    registro = ejecutar_pipeline(url, secreto)
    return 0 if registro["resultado"] == PROMOCIONADO else 1


if __name__ == "__main__":
    sys.exit(main())
