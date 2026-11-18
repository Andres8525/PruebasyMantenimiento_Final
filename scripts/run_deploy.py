"""Semana 9 — Ejecuta el pipeline de CD contra un Staging real y guarda la evidencia.

Levanta src/semana9/main.py como Staging en un puerto libre (proceso nuevo, así
siempre corre la última versión del código), ejecuta el Smoke Test y decide
promoción o rollback. El resultado se agrega a reports/despliegue/historial.json.

Escenarios (los 3 de la clase):
    python scripts/run_deploy.py --escenario exitoso   # HTTP 200 -> promoción
    python scripts/run_deploy.py --escenario fallo     # HTTP 500 -> rollback
    python scripts/run_deploy.py --escenario caido     # Staging apagado -> rollback por conexión
    python scripts/run_deploy.py --url http://host:8001/health   # Staging ya levantado

Telegram: definir TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en el entorno.
Código de salida: 0 = promocionado, 1 = rollback.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dashboard import reports  # noqa: E402
from src.semana9 import deploy  # noqa: E402

ESCENARIOS = ("exitoso", "fallo", "caido")


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def levantar_staging(saludable: bool) -> tuple[subprocess.Popen, str]:
    puerto = _puerto_libre()
    env = {**os.environ, "STAGING_HEALTHY": "true" if saludable else "false", "APP_ENV": "Staging"}
    cmd = [sys.executable, "-m", "uvicorn", "src.semana9.main:app", "--port", str(puerto), "--log-level", "warning"]
    proc = subprocess.Popen(cmd, cwd=ROOT, env=env)
    base = f"http://127.0.0.1:{puerto}"
    limite = time.time() + 15
    while time.time() < limite:
        try:
            with urlopen(f"{base}/", timeout=1):
                return proc, f"{base}/health"
        except (URLError, ConnectionError, OSError):
            time.sleep(0.2)
    proc.terminate()
    raise RuntimeError("Staging no arrancó a tiempo")


def guardar(registro: dict) -> None:
    historial = reports.load_deploys()
    historial.append(registro)
    reports.DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    reports.DEPLOY_HISTORY.write_text(json.dumps(historial[-reports.HISTORY_LIMIT:], indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--escenario", choices=ESCENARIOS, default="exitoso")
    parser.add_argument("--url", help="URL de /health de un Staging ya levantado")
    args = parser.parse_args(argv)

    secreto = os.getenv("API_SECRET_KEY") or deploy.SECRETO_DEFECTO
    staging = None
    if args.url:
        url = args.url
    elif args.escenario == "caido":
        url = f"http://127.0.0.1:{_puerto_libre()}/health"  # puerto sin servidor
    else:
        staging, url = levantar_staging(saludable=args.escenario == "exitoso")

    try:
        registro = deploy.ejecutar_pipeline(url, secreto)
    finally:
        if staging:
            staging.terminate()
            staging.wait(timeout=10)

    registro["escenario"] = "externo" if args.url else args.escenario
    registro["origen"] = "GitHub Actions" if os.getenv("GITHUB_ACTIONS") else "local"
    guardar(registro)
    return 0 if registro["resultado"] == deploy.PROMOCIONADO else 1


if __name__ == "__main__":
    sys.exit(main())
