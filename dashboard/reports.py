"""Lectura de los reportes generados por Pytest (JUnit XML + coverage JSON),
flake8 (Semana 7), Locust (Semana 8) y el pipeline de CD (Semana 9), más el historial de ejecuciones.
Lo usan los scripts de scripts/ y el dashboard.
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
COVERAGE_XML = LATEST_DIR / "coverage.xml"
HTMLCOV_DIR = LATEST_DIR / "htmlcov"
LINT_FILE = LATEST_DIR / "flake8.txt"
META_FILE = LATEST_DIR / "meta.json"
HISTORY_FILE = REPORTS_DIR / "history.json"

LOAD_DIR = REPORTS_DIR / "carga"
LOAD_SUMMARY = LOAD_DIR / "summary.json"
LOAD_HTML = LOAD_DIR / "locust.html"

DEPLOY_DIR = REPORTS_DIR / "despliegue"
DEPLOY_HISTORY = DEPLOY_DIR / "historial.json"

COVERAGE_THRESHOLD = 80.0
HISTORY_LIMIT = 50
LINT_FORMAT = "%(path)s|%(row)d|%(col)d|%(code)s|%(text)s"

# Umbrales de la prueba de carga (Semana 8): p95 máximo por endpoint, en ms
LOAD_P95_MS = {"/fast": 500, "/slow": 1500}

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
    "4": {
        "titulo": "Cultura DevOps y Docker",
        "tecnica": "Dockerfile qa-runner, contenedor efímero, exit code 0",
        "modulo": "src/semana4/app.py",
    },
    "5": {
        "titulo": "Pruebas de API en Contenedores",
        "tecnica": "Requests + JSON Schema + Docker Compose",
        "modulo": "src/semana5/main.py",
    },
    "6": {
        "titulo": "Integración Continua (CI)",
        "tecnica": "GitHub Actions: push, build y pruebas automáticas",
        "modulo": "src/semana6/main.py",
    },
    "7": {
        "titulo": "Análisis Estático y Quality Gates",
        "tecnica": "flake8 + SonarCloud en el pipeline",
        "modulo": "src/semana7/calculadora.py",
    },
    "8": {
        "titulo": "Pruebas de Carga con Locust",
        "tecnica": "Enjambre de usuarios concurrentes, latencia y RPS",
        "modulo": "src/semana8/api.py",
    },
    "9": {
        "titulo": "Despliegue Continuo (CD)",
        "tecnica": "Smoke Test en Staging, rollback automático, secrets y Telegram",
        "modulo": "src/semana9/",
    },
    "10": {
        "titulo": "Infraestructura como Código (IaC)",
        "tecnica": "Docker Compose + LocalStack (S3 y SQS), aprovisionamiento idempotente",
        "modulo": "src/semana10/init_infra.py",
    },
}

# Textos explicativos por semana: qué demuestra, cómo leer sus resultados y cómo ejecutarla
DETALLES = {
    "1": {
        "objetivo": "Comprueba la regla de acceso (18 años o más) con pruebas escritas en tres pasos: "
                    "preparar los datos, ejecutar la función y verificar el resultado (patrón AAA).",
        "lectura": "Cada fila es una prueba. Aprobada significa que la función devolvió lo esperado; "
                   "fallida muestra el valor obtenido y el motivo.",
        "comando": "python -m pytest -m semana1 -v --no-cov",
    },
    "2": {
        "objetivo": "Prueba los bordes de cada regla (17/18, 65/66, 599/600, 2.9/3.0) y las entradas inválidas. "
                    "Una sola función de prueba recibe muchos datos gracias a la parametrización.",
        "lectura": "La columna Datos de entrada muestra los valores de cada caso. Los casos de error verifican "
                   "que la función rechace negativos, texto o valores fuera de rango.",
        "comando": "python -m pytest -m semana2 -v --no-cov",
    },
    "3": {
        "objetivo": "Mide qué porcentaje del código ejecutan las pruebas. Si queda por debajo del 80%, "
                    "el Quality Gate rechaza la entrega aunque todas las pruebas pasen.",
        "lectura": "La barra de cada módulo indica su cobertura; la columna Líneas sin probar señala "
                   "el código que ninguna prueba ejecutó.",
        "comando": "python scripts/run_tests.py -m semana1   (demostración del rechazo)",
    },
    "4": {
        "objetivo": "Las pruebas se empaquetan en la imagen inmutable qa-runner y se ejecutan en un contenedor "
                    "efímero. Código de salida 0 significa listo para integrarse.",
        "lectura": "Los resultados son los mismos en cualquier máquina porque el entorno viaja dentro de la imagen.",
        "comando": "docker build -f docker/qa.Dockerfile -t qa-runner:v1 .  &&  docker run --rm qa-runner:v1",
    },
    "5": {
        "objetivo": "Valida una API REST en tres niveles: código de estado HTTP, cabeceras y tiempo de respuesta, "
                    "y contrato de datos con JSON Schema.",
        "lectura": "Si el backend cambia un tipo de dato, la prueba de esquema falla antes de afectar al cliente.",
        "comando": "docker compose up --build --exit-code-from test-runner api-service test-runner",
    },
    "6": {
        "objetivo": "GitHub Actions ejecuta pruebas, contenedores, carga e infraestructura en cada push a main. "
                    "Si algo falla, el pipeline bloquea la entrega.",
        "lectura": "Aquí se ven las pruebas de la API base; el historial de ejecuciones del pipeline está "
                   "en la pestaña Actions del repositorio.",
        "comando": "git push origin main",
    },
    "7": {
        "objetivo": "Revisa el código sin ejecutarlo: flake8 en cada corrida y SonarCloud en el pipeline. "
                    "Cero hallazgos es la tercera condición del Quality Gate.",
        "lectura": "Cada hallazgo indica archivo, línea, regla y mensaje. Una variable sin uso (F841) "
                   "basta para rechazar la entrega.",
        "comando": "python -m flake8 .",
    },
    "8": {
        "objetivo": "Simula usuarios concurrentes con Locust para medir latencia y peticiones por segundo, "
                    "y evidenciar el cuello de botella del endpoint /slow.",
        "lectura": "Latencia: cuánto tarda una petición (p95 = el 95% tarda menos que ese valor). "
                   "Throughput: peticiones atendidas por segundo.",
        "comando": "python scripts/run_load_test.py -u 200 -r 20 -t 30",
    },
    "9": {
        "objetivo": "Antes de llegar a Producción, Staging debe responder HTTP 200. Si falla, el pipeline "
                    "revierte automáticamente a la versión estable y avisa por Telegram.",
        "lectura": "Promocionado: el cambio llegó a Producción. Rollback: el fallo quedó aislado en Staging. "
                   "El secreto siempre se muestra enmascarado.",
        "comando": "python scripts/run_deploy.py --escenario exitoso | fallo | caido",
    },
    "10": {
        "objetivo": "La infraestructura (bucket S3 y cola SQS) se declara y crea con código en LocalStack, "
                    "una nube AWS emulada en Docker. Ejecutarlo varias veces deja el mismo resultado.",
        "lectura": "Las pruebas de integración solo se ejecutan con LocalStack encendido; si está apagado "
                   "aparecen como omitidas.",
        "comando": "docker compose --profile iac up -d localstack  &&  python -m src.semana10.init_infra",
    },
}

BLOQUES = [
    {"id": "bloque-1", "titulo": "Fundamentos de pruebas", "responsable": "Diego", "semanas": ["1", "2", "3"]},
    {"id": "bloque-2", "titulo": "Contenedores e integración continua", "responsable": "Jhoan",
     "semanas": ["4", "5", "6"]},
    {"id": "bloque-3", "titulo": "Calidad, rendimiento y entrega", "responsable": "Edison",
     "semanas": ["7", "8", "9", "10"]},
]

REPO_ACTIONS_URL = "https://github.com/Andres8525/PruebasyMantenimiento_Final/actions"

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


def _orden_natural(texto: str) -> list:
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", texto)]


def parse_coverage(path: Path = COVERAGE_FILE) -> dict:
    if not path.exists():
        return {"total": None, "archivos": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    archivos = []
    for nombre, info in sorted(data.get("files", {}).items(), key=lambda kv: _orden_natural(kv[0])):
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


def parse_lint(path: Path = LINT_FILE) -> dict:
    """Hallazgos de flake8 (formato LINT_FORMAT). ejecutado=False si no corrió."""
    if not path.exists():
        return {"ejecutado": False, "hallazgos": []}
    hallazgos = []
    for linea in path.read_text(encoding="utf-8").splitlines():
        partes = linea.split("|", 4)
        if len(partes) != 5:
            continue
        ruta, fila, col, codigo, texto = partes
        hallazgos.append(
            {
                "archivo": ruta.replace("\\", "/").lstrip("./"),
                "linea": int(fila),
                "columna": int(col),
                "codigo": codigo,
                "mensaje": texto,
            }
        )
    return {"ejecutado": True, "hallazgos": hallazgos}


def load_load_summary() -> dict | None:
    if not LOAD_SUMMARY.exists():
        return None
    try:
        return json.loads(LOAD_SUMMARY.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def load_deploys() -> list[dict]:
    if not DEPLOY_HISTORY.exists():
        return []
    try:
        return json.loads(DEPLOY_HISTORY.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def build_summary() -> dict:
    """Resumen completo de la última ejecución, listo para el dashboard."""
    casos = parse_junit()
    cobertura = parse_coverage()
    lint = parse_lint()
    meta = json.loads(META_FILE.read_text(encoding="utf-8")) if META_FILE.exists() else {}

    conteo = {k: sum(1 for c in casos if c["estado"] == k) for k in ("passed", "failed", "error", "skipped")}
    total = len(casos)
    ejecutadas = total - conteo["skipped"]
    tasa = round(100 * conteo["passed"] / ejecutadas, 1) if ejecutadas else 0.0

    semanas = []
    claves = sorted({c["semana"] for c in casos} | set(SEMANAS), key=lambda s: (not s.isdigit(), s.zfill(3)))
    for clave in claves:
        propios = [c for c in casos if c["semana"] == clave]
        info = {**SEMANAS.get(clave, {"titulo": "Otras pruebas", "tecnica": "", "modulo": ""}),
                **DETALLES.get(clave, {})}
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
    lint_ok = lint["ejecutado"] and not lint["hallazgos"]

    resumen = {
        "hay_datos": total > 0,
        "meta": meta,
        "total": total,
        **conteo,
        "tasa_exito": tasa,
        "duracion": round(sum(c["tiempo"] for c in casos), 2),
        "cobertura": cobertura,
        "lint": lint,
        "umbral": COVERAGE_THRESHOLD,
        "gate": {
            "cobertura_ok": gate_cobertura,
            "pruebas_ok": sin_fallos,
            "lint_ok": lint_ok,
            "aprobado": gate_cobertura and sin_fallos and lint_ok,
        },
        "semanas": semanas,
        "historial": load_history(),
        "carga": load_load_summary(),
        "despliegues": load_deploys(),
        "bloques": BLOQUES,
        "repo_actions": REPO_ACTIONS_URL,
    }
    resumen["por_semana"] = {s["clave"]: s for s in semanas}
    resumen["etapas"] = calcular_etapas(resumen)
    return resumen


def _estado_semanas(semanas: list[dict], claves: list[str]) -> str:
    propias = [s for s in semanas if s["clave"] in claves]
    if not any(s["total"] for s in propias):
        return "pendiente"
    return "fallo" if any(s["fallidas"] for s in propias) else "ok"


def _estado_etapa(condicion_ejecutada: bool, condicion_ok: bool) -> str:
    if not condicion_ejecutada:
        return "pendiente"
    return "ok" if condicion_ok else "fallo"


def calcular_etapas(resumen: dict) -> list[dict]:
    """Estado de cada etapa del flujo DevOps, en el orden en que se construyó durante el curso."""
    semanas = resumen["semanas"]
    carga = resumen["carga"]
    despliegues = resumen["despliegues"]
    gate = resumen["gate"]
    return [
        {"id": "etapa-pruebas", "nombre": "Pruebas unitarias", "semanas": "Semanas 1-2",
         "estado": _estado_semanas(semanas, ["1", "2"])},
        {"id": "etapa-cobertura", "nombre": "Cobertura", "semanas": "Semana 3",
         "estado": _estado_etapa(resumen["hay_datos"], gate["cobertura_ok"])},
        {"id": "etapa-contenedores", "nombre": "Contenedores", "semanas": "Semanas 4-5",
         "estado": _estado_semanas(semanas, ["4", "5"])},
        {"id": "etapa-ci", "nombre": "Integración continua", "semanas": "Semana 6",
         "estado": _estado_semanas(semanas, ["6"])},
        {"id": "etapa-estatico", "nombre": "Análisis estático", "semanas": "Semana 7",
         "estado": _estado_etapa(resumen["lint"]["ejecutado"], gate["lint_ok"])},
        {"id": "etapa-carga", "nombre": "Prueba de carga", "semanas": "Semana 8",
         "estado": _estado_etapa(carga is not None, bool(carga and carga["aprobado"]))},
        {"id": "etapa-despliegue", "nombre": "Despliegue", "semanas": "Semana 9",
         "estado": _estado_etapa(bool(despliegues),
                                 bool(despliegues) and despliegues[-1]["resultado"] == "PROMOCIONADO")},
        {"id": "etapa-iac", "nombre": "Infraestructura", "semanas": "Semana 10", "estado": "pendiente"},
    ]


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
