# Proyecto Final — Pruebas y Mantenimiento de Software (DevOps)

Universidad Cooperativa de Colombia · Docente: Mg. Gabriel Guerrero Arellano

Este proyecto reúne en un solo repositorio **todos los laboratorios de la materia**.
Incluye un **Dashboard de Calidad** donde se ven todas las pruebas de cada clase, la
cobertura de código, el Quality Gate y el historial de ejecuciones.

## Qué se vio en cada clase

| Semana | Tema | Código | Pruebas |
|---|---|---|---|
| 1 | Patrón AAA, Pytest, terminal verde vs. roja | `src/semana1/sistema.py` | `tests/semana1/test_sistema.py` |
| 2 | Partición de Equivalencia, BVA, `@pytest.mark.parametrize`, `pytest.raises` | `src/semana2/` (edad, crédito bancario, notas) | `tests/semana2/` |
| 3 | Cobertura de código y Quality Gate (`--cov-fail-under=80`) | `src/semana3/validator.py` | `tests/semana3/test_validator.py` |
| 4 | Cultura DevOps y Docker | `docker/`, `docker-compose.yml` | — |
| 5 | Pruebas de API en contenedores (Requests + JSON Schema) | `src/semana5/main.py` (FastAPI) | `tests/semana5/test_api.py` |
| 11 | Integración Continua | `.github/workflows/ci.yml` | — |

## Estructura

```
Final_Devops/
├── src/                      # Código de negocio, un paquete por semana
│   ├── semana1/sistema.py
│   ├── semana2/modulo_sistema.py · validador_credito.py · notas.py
│   ├── semana3/validator.py
│   └── semana5/main.py       # API FastAPI (/health, /api/v1/users)
├── tests/                    # Suites de Pytest, una carpeta por semana
│   ├── conftest.py           # marca cada prueba con su semana (-m semana2)
│   └── semana1/ semana2/ semana3/ semana5/
├── dashboard/                # Dashboard de calidad (FastAPI + Jinja2)
│   ├── app.py
│   ├── reports.py            # lee JUnit XML + coverage JSON + historial
│   └── templates/index.html
├── scripts/run_tests.py      # ejecuta la suite y genera los reportes
├── config/coverage-remote.cfg
├── docker/                   # api.Dockerfile · qa.Dockerfile
├── docker-compose.yml        # api-service + test-runner + dashboard
├── .github/workflows/ci.yml  # pipeline CI con Quality Gate
├── pytest.ini · .coveragerc · requirements.txt
└── reports/                  # salida generada (no se versiona)
```

## Uso local (sin Docker)

```powershell
python -m venv venv
.\venv\Scripts\activate
python -m pip install -r requirements.txt

# 1) Solo pruebas, como en clase (incluye el Quality Gate)
python -m pytest -v

# 2) Pruebas + reportes para el dashboard
python scripts/run_tests.py
python scripts/run_tests.py -m semana2     # una sola semana

# 3) Dashboard
python -m uvicorn dashboard.app:app --reload --port 8080
# abrir http://localhost:8080
```

En modo local, las pruebas de la Semana 5 levantan la API automáticamente en un
puerto libre, así que no hace falta Docker para ver todo en verde.

## Uso con Docker (Semana 5)

```powershell
# Pipeline efímero: API + test-runner, devuelve el código de salida de las pruebas
docker compose up --build --exit-code-from test-runner api-service test-runner

# Dashboard en contenedor (http://localhost:8080)
docker compose up --build dashboard

docker compose down
```

Con `API_URL` definido, las pruebas de la API apuntan al contenedor `api-service`
y la cobertura excluye `src/semana5` (ese código corre en otro contenedor).

## Quality Gate

El build se aprueba solo si se cumplen las dos condiciones:

1. **0 pruebas fallidas**
2. **Cobertura ≥ 80%** sobre `src/` (líneas + ramas)

Demostración del rechazo (como en la Semana 3): `python scripts/run_tests.py -m semana1`
ejecuta solo 4 pruebas, la cobertura cae a ~12% y el Gate queda **RECHAZADO**.

## Inyección de fallas (para la sustentación)

| Clase | Cambio | Prueba que se pone roja |
|---|---|---|
| 1 | `edad >= 18` → `edad > 18` en `sistema.py` | `test_acceso_exactamente_18` |
| 2 | `ingresos >= 2000.0` → `ingresos > 2000.0` | `test_evaluar_prestamo_fronteras[700-2000.0-APROBADO]` |
| 5 | `"active": True` → `"active": "SI"` en `main.py` | `test_get_users_schema_validation` |

Después de cada cambio, pulsa **Ejecutar pruebas** en el dashboard y verás el fallo con su mensaje.
