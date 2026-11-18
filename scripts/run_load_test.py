"""Semana 8 — Prueba de carga con Locust en modo headless (sin interfaz).

Levanta la API objetivo (src/semana8/api.py) en un puerto libre, lanza el enjambre
de load/locustfile.py y guarda en reports/carga/: los CSV de Locust, el reporte
HTML y summary.json (lo que muestra el dashboard).

Uso:
    python scripts/run_load_test.py                       # 200 usuarios, 30 s
    python scripts/run_load_test.py -u 100 -r 10 -t 60
    python scripts/run_load_test.py --host http://api:8000  # contra una API ya levantada

Código de salida: 0 si no hubo fallos y el p95 de cada endpoint está bajo su umbral.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dashboard import reports  # noqa: E402

CSV_PREFIX = reports.LOAD_DIR / "locust"


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def levantar_api() -> tuple[subprocess.Popen, str]:
    puerto = _puerto_libre()
    cmd = [sys.executable, "-m", "uvicorn", "src.semana8.api:app", "--port", str(puerto), "--log-level", "warning"]
    proc = subprocess.Popen(cmd, cwd=ROOT)
    url = f"http://127.0.0.1:{puerto}"
    limite = time.time() + 15
    while time.time() < limite:
        try:
            with urlopen(f"{url}/fast", timeout=1):
                return proc, url
        except (URLError, ConnectionError, OSError):
            time.sleep(0.2)
    proc.terminate()
    raise RuntimeError("La API objetivo no arrancó a tiempo")


def _num(valor: str) -> float:
    try:
        return round(float(valor), 2)
    except (TypeError, ValueError):
        return 0.0


def leer_estadisticas() -> list[dict]:
    filas = []
    with open(f"{CSV_PREFIX}_stats.csv", encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            filas.append(
                {
                    "nombre": fila["Name"],
                    "peticiones": int(fila["Request Count"]),
                    "fallos": int(fila["Failure Count"]),
                    "mediana_ms": _num(fila["Median Response Time"]),
                    "promedio_ms": _num(fila["Average Response Time"]),
                    "min_ms": _num(fila["Min Response Time"]),
                    "max_ms": _num(fila["Max Response Time"]),
                    "p95_ms": _num(fila["95%"]),
                    "p99_ms": _num(fila["99%"]),
                    "rps": _num(fila["Requests/s"]),
                }
            )
    return filas


def leer_serie() -> list[dict]:
    """Serie temporal agregada (pestaña Charts de Locust)."""
    ruta = Path(f"{CSV_PREFIX}_stats_history.csv")
    if not ruta.exists():
        return []
    serie = []
    with open(ruta, encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            if fila["Name"] != "Aggregated":
                continue
            serie.append(
                {
                    "t": int(fila["Timestamp"]),
                    "usuarios": int(fila["User Count"]),
                    "rps": _num(fila["Requests/s"]),
                    "fallos_s": _num(fila["Failures/s"]),
                    "p50_ms": _num(fila["50%"]),
                    "p95_ms": _num(fila["95%"]),
                }
            )
    if serie:
        t0 = serie[0]["t"]
        for punto in serie:
            punto["t"] -= t0
    return serie


def evaluar(endpoints: list[dict]) -> list[dict]:
    checks = []
    total = next((e for e in endpoints if e["nombre"] == "Aggregated"), None)
    if total:
        checks.append({"regla": "0 peticiones fallidas", "ok": total["fallos"] == 0,
                       "valor": f"{total['fallos']} fallos"})
    for nombre, umbral in reports.LOAD_P95_MS.items():
        e = next((x for x in endpoints if x["nombre"] == nombre), None)
        if e:
            checks.append({"regla": f"p95 de {nombre} < {umbral} ms", "ok": e["p95_ms"] < umbral,
                           "valor": f"{e['p95_ms']} ms"})
    return checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-u", "--usuarios", type=int, default=200, help="Usuarios concurrentes (por defecto 200)")
    parser.add_argument("-r", "--ritmo", type=int, default=20, help="Usuarios nuevos por segundo (spawn rate)")
    parser.add_argument("-t", "--duracion", type=int, default=30, help="Duración en segundos")
    parser.add_argument("--host", help="API ya levantada; si se omite se arranca src/semana8/api.py")
    args = parser.parse_args(argv)

    if reports.LOAD_DIR.exists():
        shutil.rmtree(reports.LOAD_DIR)
    reports.LOAD_DIR.mkdir(parents=True)

    api_proc = None
    host = args.host
    if not host:
        api_proc, host = levantar_api()

    inicio = datetime.now()
    try:
        cmd = [
            sys.executable, "-m", "locust", "-f", "load/locustfile.py", "--headless",
            "-u", str(args.usuarios), "-r", str(args.ritmo), "-t", f"{args.duracion}s",
            "--host", host, "--csv", str(CSV_PREFIX), "--csv-full-history",
            "--html", str(reports.LOAD_HTML), "--only-summary",
        ]
        print("$", " ".join(cmd), flush=True)
        codigo_locust = subprocess.call(cmd, cwd=ROOT)
    finally:
        if api_proc:
            api_proc.terminate()
            api_proc.wait(timeout=10)

    endpoints = leer_estadisticas()
    checks = evaluar(endpoints)
    aprobado = bool(checks) and all(c["ok"] for c in checks)
    resumen = {
        "fecha": inicio.isoformat(timespec="seconds"),
        "host": "API local (src/semana8/api.py)" if api_proc else host,
        "usuarios": args.usuarios,
        "ritmo": args.ritmo,
        "duracion_s": args.duracion,
        "codigo_locust": codigo_locust,
        "endpoints": endpoints,
        "serie": leer_serie(),
        "checks": checks,
        "aprobado": aprobado,
    }
    reports.LOAD_SUMMARY.write_text(json.dumps(resumen, indent=2), encoding="utf-8")

    for c in checks:
        print(f"  {'OK ' if c['ok'] else 'FALLO'} {c['regla']} ({c['valor']})")
    print(f"\nPrueba de carga: {'APROBADA' if aprobado else 'RECHAZADA'}", flush=True)
    return 0 if aprobado else 1


if __name__ == "__main__":
    sys.exit(main())
