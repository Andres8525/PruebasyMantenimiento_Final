"""Dashboard de Calidad — muestra todas las pruebas de todas las clases.

Ejecutar:  python -m uvicorn dashboard.app:app --reload --port 8080
Abrir:     http://localhost:8080
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from dashboard import reports

BASE = Path(__file__).resolve().parent
app = FastAPI(title="Dashboard de Calidad — Pruebas y Mantenimiento")
templates = Jinja2Templates(directory=BASE / "templates")

reports.HTMLCOV_DIR.mkdir(parents=True, exist_ok=True)
reports.LOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/cobertura", StaticFiles(directory=reports.HTMLCOV_DIR, html=True, check_dir=False), name="cobertura")
app.mount("/carga", StaticFiles(directory=reports.LOAD_DIR, html=True, check_dir=False), name="carga")

FILTROS_VALIDOS = {"todas"} | {f"semana{k}" for k in reports.SEMANAS}

_estado = {"corriendo": False, "tipo": None, "inicio": None, "fin": None, "codigo": None, "salida": ""}
_lock = threading.Lock()


class RunRequest(BaseModel):
    filtro: str = "todas"


class LoadRequest(BaseModel):
    usuarios: int = Field(200, ge=1, le=2000)
    ritmo: int = Field(20, ge=1, le=500)
    duracion: int = Field(30, ge=5, le=300)


def _ejecutar(cmd: list[str]) -> None:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        cmd, cwd=reports.ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    with _lock:
        _estado.update(
            corriendo=False,
            fin=datetime.now().isoformat(timespec="seconds"),
            codigo=proc.returncode,
            salida=(proc.stdout + proc.stderr)[-20000:],
        )


def _lanzar(tipo: str, cmd: list[str]) -> None:
    with _lock:
        if _estado["corriendo"]:
            raise HTTPException(status_code=409, detail="Ya hay una ejecución en curso")
        _estado.update(
            corriendo=True, tipo=tipo, inicio=datetime.now().isoformat(timespec="seconds"),
            fin=None, codigo=None, salida="",
        )
    threading.Thread(target=_ejecutar, args=(cmd,), daemon=True).start()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"r": reports.build_summary(), "filtros": sorted(FILTROS_VALIDOS), "umbrales_carga": reports.LOAD_P95_MS},
    )


@app.get("/api/resumen")
def resumen():
    return reports.build_summary()


@app.get("/api/estado")
def estado():
    with _lock:
        return dict(_estado)


@app.post("/api/ejecutar", status_code=202)
def ejecutar(body: RunRequest):
    if body.filtro not in FILTROS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"Filtro inválido: {body.filtro}")
    cmd = [sys.executable, str(reports.ROOT / "scripts" / "run_tests.py")]
    if body.filtro != "todas":
        cmd += ["-m", body.filtro]
    _lanzar("pruebas", cmd)
    return {"mensaje": "Ejecución iniciada", "filtro": body.filtro}


@app.post("/api/carga", status_code=202)
def carga(body: LoadRequest):
    cmd = [
        sys.executable, str(reports.ROOT / "scripts" / "run_load_test.py"),
        "-u", str(body.usuarios), "-r", str(body.ritmo), "-t", str(body.duracion),
    ]
    _lanzar("carga", cmd)
    return {"mensaje": "Prueba de carga iniciada", "usuarios": body.usuarios, "ritmo": body.ritmo,
            "duracion": body.duracion}


@app.get("/health")
def health():
    return {"status": "ok", "service": "quality-dashboard"}
