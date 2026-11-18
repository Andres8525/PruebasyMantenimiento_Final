# Proyecto Final — Pruebas y Mantenimiento de Software (DevOps)

Universidad Cooperativa de Colombia · Docente: Mg. Gabriel Guerrero Arellano

Este proyecto reúne en un solo repositorio **todos los laboratorios de la materia (Semanas 1 a 10)**.
Incluye un **Dashboard de Calidad** donde se ven todas las pruebas de cada clase, la
cobertura de código, el análisis estático, la prueba de carga con Locust, los despliegues continuos
(promoción / rollback), la infraestructura en LocalStack, el Quality Gate y el historial de ejecuciones.

## Qué se vio en cada clase

| Semana | Tema | Código | Pruebas / artefacto |
|---|---|---|---|
| 1 | Patrón AAA, Pytest, terminal verde vs. roja | `src/semana1/sistema.py` | `tests/semana1/` |
| 2 | Partición de Equivalencia, BVA, `@pytest.mark.parametrize`, `pytest.raises` | `src/semana2/` (edad, crédito, notas) | `tests/semana2/` |
| 3 | Cobertura de código y Quality Gate (`--cov-fail-under=80`) | `src/semana3/validator.py` | `tests/semana3/` |
| 4 | Cultura DevOps y Docker: imagen `qa-runner`, contenedor efímero, exit code | `src/semana4/app.py` | `tests/semana4/`, `docker/qa.Dockerfile` |
| 5 | Pruebas de API en contenedores (Requests + JSON Schema + healthcheck) | `src/semana5/main.py` | `tests/semana5/`, `docker-compose.yml` |
| 6 | Integración Continua con GitHub Actions | `src/semana6/main.py` | `tests/semana6/`, `.github/workflows/ci.yml` |
| 7 | Análisis estático: flake8 + SonarCloud, acciones fijadas por SHA | `src/semana7/calculadora.py` | `tests/semana7/`, `.flake8`, `sonar-project.properties`, `.github/workflows/sonar.yml` |
| 8 | Pruebas de carga con Locust (latencia, RPS, cuello de botella) | `src/semana8/api.py` | `tests/semana8/`, `load/locustfile.py`, `scripts/run_load_test.py` |
| 9 | Despliegue Continuo: Smoke Test en Staging, rollback automático, secrets, alertas a Telegram | `src/semana9/main.py`, `src/semana9/deploy.py` | `tests/semana9/`, `scripts/run_deploy.py`, `.github/workflows/cd.yml` |
| 10 | Infraestructura como Código con Docker Compose + LocalStack (S3 y SQS) | `src/semana10/init_infra.py` | `tests/semana10/`, servicio `localstack` en `docker-compose.yml` |

## Estructura

```
Final_Devops/
├── src/semanaN/              # Código de negocio, un paquete por semana (1-8)
├── tests/semanaN/            # Suites de Pytest, una carpeta por semana
│   └── conftest.py           # marca cada prueba con su semana (-m semana4)
├── load/locustfile.py        # Semana 8: enjambre de usuarios (75% /fast, 25% /slow)
├── dashboard/                # Dashboard de calidad (FastAPI + Jinja2)
│   ├── app.py
│   ├── reports.py            # lee JUnit, cobertura, flake8, Locust e historial
│   └── templates/index.html
├── scripts/
│   ├── run_tests.py          # pruebas + linter + Quality Gate + reportes
│   ├── run_load_test.py      # prueba de carga headless con Locust
│   └── run_deploy.py         # pipeline de CD: Staging -> promoción / rollback
├── docker/                   # api.Dockerfile · qa.Dockerfile (qa-runner)
├── docker-compose.yml        # api-service + test-runner + dashboard (+ perfiles "carga" e "iac")
├── .github/workflows/
│   ├── ci.yml                # Semana 6: build-and-test, contenedores, carga e IaC
│   ├── cd.yml                # Semana 9: despliegue continuo con rollback
│   └── sonar.yml             # Semana 7: Quality Gate de SonarCloud
├── sonar-project.properties · .flake8 · pytest.ini · .coveragerc · requirements.txt
└── reports/                  # salida generada (no se versiona)
```

## Uso local (sin Docker)

```powershell
python -m venv venv
.\venv\Scripts\activate
python -m pip install -r requirements.txt

# 1) Solo pruebas, como en clase (incluye el Quality Gate de cobertura)
python -m pytest -v

# 2) Pruebas + linter + reportes para el dashboard
python scripts/run_tests.py
python scripts/run_tests.py -m semana4     # una sola semana

# 3) Prueba de carga (Semana 8): 200 usuarios, 20 nuevos/s, 30 s
python scripts/run_load_test.py
python scripts/run_load_test.py -u 100 -r 10 -t 60

# 4) Dashboard (http://localhost:8080)
python -m uvicorn dashboard.app:app --reload --port 8080
```

Desde el dashboard también se pueden lanzar las pruebas (todas o por semana) y el enjambre de Locust.

## Uso con Docker (Semanas 4 y 5)

```powershell
# Semana 4: imagen inmutable y contenedor efímero
docker build -f docker/qa.Dockerfile -t qa-runner:v1 .
docker run --rm qa-runner:v1

# Semana 5: API + test-runner en la red privada; devuelve el exit code de las pruebas
docker compose up --build --exit-code-from test-runner api-service test-runner

# Dashboard en contenedor (http://localhost:8080)
docker compose up --build dashboard

# Semana 8: interfaz web de Locust (http://localhost:8089) contra la API de carga
docker compose --profile carga up --build api-carga locust

docker compose down
```

## Integración Continua (Semana 6)

`ci.yml` se dispara en cada push o pull request a `main`:

1. **build-and-test**: instala dependencias y corre `scripts/run_tests.py` (pruebas + flake8 + Quality Gate).
2. **pruebas-contenedores**: levanta la API y el test-runner con Docker Compose.
3. **pruebas-carga**: enjambre corto de Locust (50 usuarios, 20 s) y publica el reporte.

4. **infraestructura-iac**: levanta LocalStack como servicio, aprovisiona dos veces (idempotencia) y prueba S3/SQS.

Los reportes quedan como *artifacts* del run en la pestaña **Actions**.

## Despliegue Continuo (Semana 9)

`cd.yml` se ejecuta **solo cuando el CI de `main` termina en verde** (ningún cambio llega a Producción sin
pasar por Staging). También se lanza a mano: **Actions → Pipeline Despliegue Continuo (CD) → Run workflow**,
eligiendo el escenario.

```powershell
python scripts/run_deploy.py --escenario exitoso   # Caso A: HTTP 200 -> promoción a Producción
python scripts/run_deploy.py --escenario fallo     # Caso B: HTTP 500 -> rollback automático
python scripts/run_deploy.py --escenario caido     # Staging apagado -> rollback por conexión
```

Cada ejecución levanta un Staging **nuevo** (otro proceso), así siempre corre la última versión del código:
es lo mismo que en clase se lograba con `--reload`. El laboratorio original también funciona:

```powershell
python -m uvicorn src.semana9.main:app --port 8001 --reload   # terminal 1
python -m src.semana9.deploy                                  # terminal 2
```

### Alertas a Telegram desde el celular

El token del bot **nunca va en el código** (en la diapositiva aparece escrito en `deploy.py`; aquí se lee
de variables de entorno / GitHub Secrets). Si falta, el pipeline funciona igual y omite la alerta.

1. En Telegram, busca **@BotFather** (insignia azul) → **Iniciar** → envía `/newbot`.
2. Nombre del bot, por ejemplo `DevOps Deploy Bot`. Usuario: debe terminar en `bot`, por ejemplo `ucc_final_deploy_bot`.
3. BotFather responde con el **token** (`1234567890:AA...`). Cópialo; es la contraseña del bot.
4. Toca el enlace `t.me/<tu_bot>` que te dio BotFather y pulsa **Iniciar**. Sin este paso el bot no puede escribirte.
5. Busca **@userinfobot** → **Iniciar**: te responde con tu **Id** numérico. Ese es el `TELEGRAM_CHAT_ID`.
6. En el navegador del celular abre el repo en GitHub (modo escritorio si no ves el menú) →
   **Settings → Secrets and variables → Actions → New repository secret** y crea tres secretos:
   `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` y `API_SECRET_KEY` (cualquier clave, p. ej. `clave_final_2026`).
7. Prueba: **Actions → Pipeline Despliegue Continuo (CD) → Run workflow** tres veces, con `caido`, `exitoso`
   y `fallo`. Deben llegarte las 3 alertas: 🚨 servidor inaccesible, 🚀 despliegue exitoso y 🚨 rollback.
8. Para probar desde el PC (y verlo en el dashboard):

   ```powershell
   $env:TELEGRAM_BOT_TOKEN = "<token>"; $env:TELEGRAM_CHAT_ID = "<id>"
   python scripts/run_deploy.py --escenario exitoso
   ```

   Para que el botón del dashboard también notifique, define esas variables en la misma terminal antes de
   arrancar `uvicorn dashboard.app:app`.

Si el token llega a quedar expuesto: en @BotFather → `/revoke` → elige el bot → actualiza el secreto.

## Infraestructura como Código (Semana 10)

```powershell
docker compose --profile iac up -d localstack     # nube AWS emulada en el puerto 4566
docker ps                                         # localstack_lab10 en estado Up
python -m src.semana10.init_infra                 # crea mi-bucket-pruebas y cola-notificaciones
python -m src.semana10.init_infra                 # idempotente: mismo resultado ("existente")
docker compose --profile iac down                 # destruye la nube sin dejar rastros
```

Con LocalStack arriba, las pruebas de integración de `tests/semana10` dejan de omitirse y hacen un viaje
completo por S3 (subir/leer un objeto) y SQS (enviar/recibir un mensaje). El dashboard muestra los buckets y
colas existentes y tiene un botón para aprovisionar. Se omitió `version: '3.8'` del manifiesto porque
Docker Compose v2 lo marca como obsoleto.

## SonarCloud (Semana 7)

1. Entrar a [sonarcloud.io](https://sonarcloud.io) con GitHub e importar este repositorio.
2. En el proyecto: **Administration → Analysis Method** → desactivar *Automatic Analysis* (el análisis lo hace el pipeline).
3. Copiar el token y crearlo en GitHub: **Settings → Secrets and variables → Actions → New repository secret** con nombre `SONAR_TOKEN`.
4. Verificar que `sonar.organization` y `sonar.projectKey` de `sonar-project.properties` coincidan con los de SonarCloud.

Sin el secreto, `sonar.yml` muestra una advertencia y omite el análisis, sin poner el pipeline en rojo.
Todas las acciones de los workflows están fijadas por SHA completo, que es la corrección de la regla
*"Use full commit SHA hash for this dependency"* que SonarCloud marca como vulnerabilidad alta.

## Quality Gate

El build se aprueba solo si se cumplen las tres condiciones:

1. **0 pruebas fallidas**
2. **Cobertura ≥ 80%** sobre `src/` (líneas + ramas)
3. **0 hallazgos de flake8** (análisis estático)

La prueba de carga tiene su propio veredicto: 0 peticiones fallidas, p95 de `/fast` < 500 ms y p95 de `/slow` < 1500 ms.

Demostración del rechazo (Semana 3): `python scripts/run_tests.py -m semana1` ejecuta solo 4 pruebas,
la cobertura cae a ~20% y el Gate queda **RECHAZADO**.

## Inyección de fallas (para la sustentación)

| Clase | Cambio | Qué se pone rojo |
|---|---|---|
| 1 | `edad >= 18` → `edad > 18` en `sistema.py` | `test_acceso_exactamente_18` |
| 2 | `ingresos >= 2000.0` → `ingresos > 2000.0` | `test_evaluar_prestamo_fronteras[700-2000.0-APROBADO]` |
| 4 | descuento del estudiante `50.0` → `40.0` en `app.py` ("Break the Container") | `test_descuento_estudiante_alta_cobertura`, exit code 1 |
| 5 | `"active": True` → `"active": "SI"` en `main.py` | `test_get_users_schema_validation` |
| 7 | agregar a `calculadora.py` una variable sin uso (`descuento_fantasma = 0.10`) | flake8 `F841` → Quality Gate rechazado |
| 8 | subir `RETARDO_SLOW_SEGUNDOS` a `2` en `semana8/api.py` | prueba de carga: p95 de `/slow` supera el umbral |
| 9 | `IS_HEALTHY = False` en `semana9/main.py` | Smoke Test HTTP 500 → rollback automático y alerta 🚨 |

Después de cada cambio, pulsa **Ejecutar pruebas** (o **Lanzar enjambre**) en el dashboard y verás el fallo con su mensaje.
