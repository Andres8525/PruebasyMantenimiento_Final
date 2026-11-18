"""Ejecuta la suite completa + el linter y deja los reportes que consume el dashboard.

Uso:
    python scripts/run_tests.py                 # todas las semanas
    python scripts/run_tests.py -m semana2      # solo una semana
    python scripts/run_tests.py -- -x           # argumentos extra para pytest

Genera en reports/latest/: junit.xml, coverage.json, coverage.xml (SonarCloud),
htmlcov/, flake8.txt y meta.json, y agrega un resumen a reports/history.json.

Código de salida: 0 solo si el Quality Gate completo pasa (pruebas + cobertura
+ 0 hallazgos del linter). Así sirve como paso de CI/CD.
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

LINT_TARGETS = ["src", "tests", "dashboard", "scripts", "load"]


def ejecutar_pytest(marker: str | None, extra: list[str], modo: str) -> int:
    cmd = [
        sys.executable, "-m", "pytest", "-v",
        f"--junitxml={reports.JUNIT_FILE}",
        f"--cov-report=json:{reports.COVERAGE_FILE}",
        f"--cov-report=xml:{reports.COVERAGE_XML}",
        f"--cov-report=html:{reports.HTMLCOV_DIR}",
    ]
    if modo == "contenedor":
        cmd.append("--cov-config=config/coverage-remote.cfg")
    if marker:
        cmd += ["-m", marker]
    cmd += extra
    print("$", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=ROOT)


def ejecutar_linter() -> int:
    """Semana 7: análisis estático rápido con flake8 (no ejecuta el código)."""
    cmd = [sys.executable, "-m", "flake8", f"--format={reports.LINT_FORMAT}", "--exit-zero", *LINT_TARGETS]
    print("$", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    reports.LINT_FILE.write_text(proc.stdout, encoding="utf-8")
    hallazgos = reports.parse_lint()["hallazgos"]
    for h in hallazgos:
        print(f"  {h['archivo']}:{h['linea']}:{h['columna']} {h['codigo']} {h['mensaje']}")
    print(f"flake8: {len(hallazgos)} hallazgo(s)", flush=True)
    return len(hallazgos)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-m", "--marker", help="Filtra por semana, p. ej. semana2")
    parser.add_argument("extra", nargs="*", help="Argumentos adicionales para pytest (después de --)")
    args = parser.parse_args(argv)

    if reports.LATEST_DIR.exists():
        shutil.rmtree(reports.LATEST_DIR)
    reports.LATEST_DIR.mkdir(parents=True)

    modo = "contenedor" if os.getenv("API_URL") else "local"
    inicio = datetime.now()
    codigo_pytest = ejecutar_pytest(args.marker, args.extra, modo)
    num_hallazgos = ejecutar_linter()

    resumen_previo = {
        "fecha": inicio.isoformat(timespec="seconds"),
        "modo": modo,
        "filtro": args.marker or "todas",
        "codigo_pytest": codigo_pytest,
    }
    reports.META_FILE.write_text(json.dumps(resumen_previo, indent=2), encoding="utf-8")

    resumen = reports.build_summary()
    aprobado = resumen["gate"]["aprobado"]
    reports.append_history(
        {
            **resumen_previo,
            "total": resumen["total"],
            "passed": resumen["passed"],
            "failed": resumen["failed"] + resumen["error"],
            "skipped": resumen["skipped"],
            "tasa_exito": resumen["tasa_exito"],
            "cobertura": resumen["cobertura"]["total"],
            "lint": num_hallazgos,
            "gate_aprobado": aprobado,
        }
    )
    print(
        f"\nQuality Gate: {'APROBADO' if aprobado else 'RECHAZADO'} - "
        f"{resumen['passed']}/{resumen['total']} pruebas, cobertura {resumen['cobertura']['total']}%, "
        f"{num_hallazgos} hallazgo(s) de flake8",
        flush=True,
    )
    return 0 if aprobado else (codigo_pytest or 1)


if __name__ == "__main__":
    sys.exit(main())
