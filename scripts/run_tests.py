"""Ejecuta la suite completa y deja los reportes que consume el dashboard.

Uso:
    python scripts/run_tests.py                 # todas las semanas
    python scripts/run_tests.py -m semana2      # solo una semana
    python scripts/run_tests.py -- -x           # argumentos extra para pytest

Genera en reports/latest/: junit.xml, coverage.json, htmlcov/ y meta.json,
y agrega un resumen a reports/history.json. Devuelve el código de salida de
Pytest (0 = verde), así sirve como paso de CI/CD.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dashboard import reports  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-m", "--marker", help="Filtra por semana, p. ej. semana2")
    parser.add_argument("extra", nargs="*", help="Argumentos adicionales para pytest (después de --)")
    args = parser.parse_args(argv)

    if reports.LATEST_DIR.exists():
        shutil.rmtree(reports.LATEST_DIR)
    reports.LATEST_DIR.mkdir(parents=True)

    modo = "contenedor" if os.getenv("API_URL") else "local"
    cmd = [
        sys.executable, "-m", "pytest", "-v",
        f"--junitxml={reports.JUNIT_FILE}",
        f"--cov-report=json:{reports.COVERAGE_FILE}",
        f"--cov-report=html:{reports.HTMLCOV_DIR}",
    ]
    if modo == "contenedor":
        cmd.append("--cov-config=config/coverage-remote.cfg")
    if args.marker:
        cmd += ["-m", args.marker]
    cmd += args.extra

    inicio = datetime.now()
    print("$", " ".join(cmd), flush=True)
    codigo = subprocess.call(cmd, cwd=ROOT)

    meta = {
        "fecha": inicio.isoformat(timespec="seconds"),
        "modo": modo,
        "filtro": args.marker or "todas",
        "codigo_salida": codigo,
    }
    reports.META_FILE.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    resumen = reports.build_summary()
    reports.append_history(
        {
            **meta,
            "total": resumen["total"],
            "passed": resumen["passed"],
            "failed": resumen["failed"] + resumen["error"],
            "skipped": resumen["skipped"],
            "tasa_exito": resumen["tasa_exito"],
            "cobertura": resumen["cobertura"]["total"],
            "gate_aprobado": resumen["gate"]["aprobado"],
        }
    )
    estado = "APROBADO" if resumen["gate"]["aprobado"] else "RECHAZADO"
    print(f"\nQuality Gate: {estado} - {resumen['passed']}/{resumen['total']} pruebas, "
          f"cobertura {resumen['cobertura']['total']}%", flush=True)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
