"""Lectura de los reportes generados por Pytest (JUnit XML + coverage JSON)
e historial de ejecuciones. Lo usan tanto scripts/run_tests.py como el dashboard.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"
LATEST_DIR = REPORTS_DIR / "latest"
JUNIT_FILE = LATEST_DIR / "junit.xml"
COVERAGE_FILE = LATEST_DIR / "coverage.json"
HTMLCOV_DIR = LATEST_DIR / "htmlcov"
META_FILE = LATEST_DIR / "meta.json"
HISTORY_FILE = REPORTS_DIR / "history.json"

COVERAGE_THRESHOLD = 80.0
HISTORY_LIMIT = 50

# Catálogo de clases: qué se vio en cada semana (fuente: PDFs de la materia)
SEMANAS = {
    "1": {
        "titulo": "Patrón AAA y Pytest",
        "tecnica": "Arrange · Act · Assert, terminal verde vs. roja",
        "modulo": "src/semana1/sistema.py",
    },
    "2": {
        "titulo": "Valores Límite y Parametrización",
        "tecnica": "EP + BVA con @pytest.mark.parametrize y pytest.raises",
        "modulo": "src/semana2/",
    },
    "3": {
        "titulo": "Cobertura y Quality Gates",
        "tecnica": "pytest-cov con --cov-fail-under=80",
        "modulo": "src/semana3/validator.py",
    },
    "5": {
        "titulo": "Pruebas de API en Contenedores",
        "tecnica": "Requests + JSON Schema + Docker Compose",
        "modulo": "src/semana5/main.py",
    },
}

_SEMANA = re.compile(r"semana(\d+)")


def _estado(testcase: ET.Element) -> tuple[str, str]:
    for tag, estado in (("failure", "failed"), ("error", "error"), ("skipped", "skipped")):
        nodo = testcase.find(tag)
        if nodo is not None:
            detalle = (nodo.get("message") or "") + "\n" + (nodo.text or "")
            return estado, detalle.strip()
    return "passed", ""


def parse_junit(path: Path = JUNIT_FILE) -> list[dict]:
    """Devuelve una lista plana de casos de prueba."""
    if not path.exists():
        return []
    casos = []
    for tc in ET.parse(path).getroot().iter("testcase"):
        clase = tc.get("classname", "")
        nombre = tc.get("name", "")
        funcion, _, params = nombre.partition("[")
        estado, detalle = _estado(tc)
        semana = _SEMANA.search(clase)
        casos.append(
            {
                "semana": semana.group(1) if semana else "otros",
                "archivo": clase.replace(".", "/") + ".py",
                "funcion": funcion,
                "parametros": params.rstrip("]"),
                "estado": estado,
                "detalle": detalle,
                "tiempo": float(tc.get("time") or 0),
            }
        )
    return casos


def parse_coverage(path: Path = COVERAGE_FILE) -> dict:
    if not path.exists():
        return {"total": None, "archivos": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    archivos = []
    for nombre, info in sorted(data.get("files", {}).items()):
        resumen = info["summary"]
        if resumen.get("num_statements", 0) == 0:
            continue  # __init__.py vacíos
        archivos.append(
            {
                "archivo": nombre.replace("\\", "/"),
                "porcentaje": round(resumen["percent_covered"], 1),
                "sentencias": resumen["num_statements"],
                "faltantes": info.get("missing_lines", []),
                "ramas": resumen.get("num_branches", 0),
                "ramas_parciales": resumen.get("num_partial_branches", 0),
            }
        )
    return {"total": round(data["totals"]["percent_covered"], 2), "archivos": archivos}


def build_summary() -> dict:
    """Resumen completo de la última ejecución, listo para el dashboard."""
    casos = parse_junit()
    cobertura = parse_coverage()
    meta = json.loads(META_FILE.read_text(encoding="utf-8")) if META_FILE.exists() else {}

    conteo = {k: sum(1 for c in casos if c["estado"] == k) for k in ("passed", "failed", "error", "skipped")}
    total = len(casos)
    ejecutadas = total - conteo["skipped"]
    tasa = round(100 * conteo["passed"] / ejecutadas, 1) if ejecutadas else 0.0

    semanas = []
    claves = sorted({c["semana"] for c in casos} | set(SEMANAS), key=lambda s: (not s.isdigit(), s.zfill(3)))
    for clave in claves:
        propios = [c for c in casos if c["semana"] == clave]
        info = SEMANAS.get(clave, {"titulo": "Otras pruebas", "tecnica": "", "modulo": ""})
        semanas.append(
            {
                "clave": clave,
                **info,
                "casos": propios,
                "total": len(propios),
                "passed": sum(1 for c in propios if c["estado"] == "passed"),
                "fallidas": sum(1 for c in propios if c["estado"] in ("failed", "error")),
                "skipped": sum(1 for c in propios if c["estado"] == "skipped"),
            }
        )

    cov_total = cobertura["total"]
    gate_cobertura = cov_total is not None and cov_total >= COVERAGE_THRESHOLD
    sin_fallos = total > 0 and conteo["failed"] == 0 and conteo["error"] == 0

    return {
        "hay_datos": total > 0,
        "meta": meta,
        "total": total,
        **conteo,
        "tasa_exito": tasa,
        "duracion": round(sum(c["tiempo"] for c in casos), 2),
        "cobertura": cobertura,
        "umbral": COVERAGE_THRESHOLD,
        "gate": {
            "cobertura_ok": gate_cobertura,
            "pruebas_ok": sin_fallos,
            "aprobado": gate_cobertura and sin_fallos,
        },
        "semanas": semanas,
        "historial": load_history(),
    }


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def append_history(entry: dict) -> None:
    historial = load_history()
    historial.append(entry)
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(historial[-HISTORY_LIMIT:], indent=2), encoding="utf-8")
