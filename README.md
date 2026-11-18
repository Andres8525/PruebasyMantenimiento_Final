# Proyecto Final — Pruebas y Mantenimiento de Software (DevOps)

Universidad Cooperativa de Colombia · Docente: Mg. Gabriel Guerrero Arellano

**Equipo:** Diego (Semanas 1–3) · Jhoan (Semanas 4–6) · Edison (Semanas 7–10)

Este proyecto reúne en un solo repositorio **todos los laboratorios de la materia (Semanas 1 a 10)** y
los conecta en un flujo DevOps completo: pruebas unitarias → cobertura → contenedores → integración
continua → análisis estático → pruebas de carga → despliegue continuo con rollback → infraestructura
como código. Un **Dashboard de Calidad** muestra todo en una sola página.

Estado actual: **90 pruebas en 10 semanas**, cobertura **~98%**, **0 hallazgos** de flake8 y los
pipelines de CI/CD en verde.

## Requisitos

- Python 3.11 (funciona desde 3.8) y `pip`
- Docker Desktop (solo para las Semanas 4, 5, 8 en contenedor y 10)
- Git y una cuenta de GitHub (para CI/CD, SonarCloud y los secrets de Telegram)

## Inicio rápido

```powershell
python -m venv venv
.\venv\Scripts\activate
python -m pip install -r requirements.txt

python scripts/run_tests.py                          # pruebas + linter + Quality Gate + reportes
python -m uvicorn dashboard.app:app --port 8090      # dashboard en http://localhost:8090
```

> Se usa el puerto **8090** porque el 8080 suele estar ocupado por otros programas (Java, Tomcat, Jenkins).
> Si aparece `[Errno 13] ... no permitido por sus permisos de acceso`, el puerto está en uso: cambia el número.

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
├── src/semanaN/              # Código de negocio, un paquete por semana (1-10)
├── tests/semanaN/            # Suites de Pytest, una carpeta por semana
│   └── conftest.py           # marca cada prueba con su semana (-m semana4)
├── load/locustfile.py        # Semana 8: enjambre de usuarios (75% /fast, 25% /slow)
├── dashboard/                # Dashboard de calidad (FastAPI + Jinja2)
│   ├── app.py                # páginas y endpoints (ejecutar pruebas, carga, CD, IaC)
│   ├── reports.py            # lee JUnit, cobertura, flake8, Locust, despliegues e historial
│   └── templates/index.html
├── scripts/
│   ├── run_tests.py          # pruebas + linter + Quality Gate + reportes
│   ├── run_load_test.py      # prueba de carga headless con Locust
│   └── run_deploy.py         # pipeline de CD: Staging -> promoción / rollback
├── docker/                   # api.Dockerfile · qa.Dockerfile (qa-runner)
├── docker-compose.yml        # api-service + test-runner + dashboard (+ perfiles "carga" e "iac")
├── .github/workflows/
│   ├── ci.yml                # Semana 6: pruebas, contenedores, carga e IaC
│   ├── sonar.yml             # Semana 7: Quality Gate de SonarCloud
│   └── cd.yml                # Semana 9: despliegue continuo con rollback
├── sonar-project.properties · .flake8 · pytest.ini · .coveragerc · requirements.txt
└── reports/                  # salida generada (no se versiona)
```

## El Dashboard de Calidad

`python -m uvicorn dashboard.app:app --port 8090` → http://localhost:8090

La página está organizada en el mismo orden en que se expone el proyecto:

| Sección | Qué muestra |
|---|---|
| Barra superior | Selector de semana, botón **Ejecutar pruebas** y navegación a cada bloque |
| Resumen | Veredicto del **Quality Gate** con sus 3 condiciones, guía "Cómo leer este tablero", indicadores (pruebas, tasa de éxito, cobertura, hallazgos, duración) y el **Flujo DevOps** con el estado de sus 8 etapas |
| Semanas 1-3 · Fundamentos de pruebas (expone Diego) | Tarjetas de las semanas 1 a 3 y la tabla de **cobertura por módulo** con las líneas sin probar |
| Semanas 4-6 · Contenedores e integración continua (expone Jhoan) | Tarjetas de las semanas 4 a 6 y la tabla de workflows de GitHub Actions con enlace a sus ejecuciones |
| Semanas 7-10 · Calidad, rendimiento y entrega (expone Edison) | Hallazgos de flake8, prueba de carga con Locust (tabla y gráficas), pipeline de despliegue con sus 3 escenarios e infraestructura en LocalStack |
| Historial | Tendencia de tasa de éxito y cobertura entre ejecuciones, con tabla detallada |

Cada tarjeta de semana tiene el mismo formato: **Qué demuestra**, **Cómo leer el resultado**, el código
y el comando para ejecutarla, su panel de resultados y la lista desplegable de sus pruebas.

Para que los botones de despliegue envíen alertas, define las variables de Telegram (ver Semana 9) en la
misma terminal antes de arrancar el dashboard.

## Comandos por semana

### Semanas 1–3: pruebas, valores límite y cobertura

```powershell
python -m pytest -v                         # suite completa como en clase (incluye --cov-fail-under=80)
python -m pytest -m semana2 -v --no-cov     # una sola semana, sin el gate de cobertura
python scripts/run_tests.py                 # suite + flake8 + reportes para el dashboard
python scripts/run_tests.py -m semana1      # demo del Gate RECHAZADO: la cobertura cae a ~20%
```

### Semanas 4–5: Docker

```powershell
# Semana 4: imagen inmutable y contenedor efímero (exit code 0 = listo para CI/CD)
docker build -f docker/qa.Dockerfile -t qa-runner:v1 .
docker run --rm qa-runner:v1

# Semana 5: API + test-runner en la red privada de Docker; devuelve el exit code de las pruebas
docker compose up --build --exit-code-from test-runner api-service test-runner

# Dashboard en contenedor (http://localhost:8080)
docker compose up --build dashboard

docker compose down
```

### Semana 6: Integración Continua

`ci.yml` se dispara en cada push o pull request a `main` y tiene 4 jobs:

1. **build-and-test**: instala dependencias y corre `scripts/run_tests.py` (pruebas + flake8 + Quality Gate).
2. **pruebas-contenedores**: levanta la API y el test-runner con Docker Compose.
3. **pruebas-carga**: enjambre corto de Locust (50 usuarios, 20 s) y publica el reporte.
4. **infraestructura-iac**: levanta LocalStack como servicio, aprovisiona dos veces (idempotencia) y prueba S3/SQS.

Los reportes quedan como *artifacts* de cada run en la pestaña **Actions**.

### Semana 7: SonarCloud

1. Entrar a [sonarcloud.io](https://sonarcloud.io) con GitHub e importar este repositorio.
2. En el proyecto: **Administration → Analysis Method** → desactivar *Automatic Analysis* (el análisis lo hace el pipeline).
3. Crear el token y guardarlo en GitHub: **Settings → Secrets and variables → Actions → New repository secret** con nombre `SONAR_TOKEN`.
4. Verificar que `sonar.organization` y `sonar.projectKey` de `sonar-project.properties` coincidan con los de SonarCloud.

Sin el secreto, `sonar.yml` muestra una advertencia y omite el análisis, sin poner el pipeline en rojo.
Todas las acciones de los workflows están fijadas por SHA completo, que es la corrección de la regla
*"Use full commit SHA hash for this dependency"* que SonarCloud marca como vulnerabilidad alta.
Localmente, flake8 corre en cada `scripts/run_tests.py` y forma parte del Quality Gate.

### Semana 8: Locust

```powershell
python scripts/run_load_test.py                     # 200 usuarios, 20 nuevos/s, 30 s (headless)
python scripts/run_load_test.py -u 100 -r 10 -t 60

# Interfaz web de Locust (http://localhost:8089) como en clase
docker compose --profile carga up --build api-carga locust
```

### Semana 9: Despliegue Continuo

`cd.yml` se ejecuta **solo cuando el CI de `main` termina en verde** (ningún cambio llega a Producción sin
pasar por Staging). También se lanza a mano: **Actions → Pipeline Despliegue Continuo (CD) → Run workflow**,
eligiendo el escenario. Los escenarios de rollback terminan en rojo a propósito (exit code 1).

```powershell
python scripts/run_deploy.py --escenario exitoso   # Caso A: HTTP 200 -> promoción a Producción
python scripts/run_deploy.py --escenario fallo     # Caso B: HTTP 500 -> rollback automático
python scripts/run_deploy.py --escenario caido     # Staging apagado -> rollback por conexión
```

Cada ejecución levanta un Staging **nuevo** (otro proceso), así siempre corre la última versión del código;
en clase lo mismo se lograba con `--reload`. El laboratorio original también funciona:

```powershell
python -m uvicorn src.semana9.main:app --port 8001 --reload   # terminal 1
python -m src.semana9.deploy                                  # terminal 2
```

#### Alertas a Telegram

El token del bot **nunca va en el código** (en la diapositiva aparece escrito en `deploy.py`; aquí se lee
de variables de entorno / GitHub Secrets). Si falta, el pipeline funciona igual y omite la alerta.

1. En Telegram, busca **@BotFather** (insignia azul) → **Iniciar** → envía `/newbot`.
2. Nombre del bot, por ejemplo `DevOps Deploy Bot`. Usuario: debe terminar en `bot`, por ejemplo `ucc_final_deploy_bot`.
3. BotFather responde con el **token** (`1234567890:AA...`). Cópialo; es la contraseña del bot.
4. Abre el enlace `t.me/...` que te dio BotFather y pulsa **Iniciar**. Sin este paso el bot no puede escribirte.
5. Busca **@userinfobot** → **Iniciar**: te responde con tu **Id** numérico. Ese es el `TELEGRAM_CHAT_ID`.
6. En GitHub: **Settings → Secrets and variables → Actions → New repository secret** y crea tres secretos:
   `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` y `API_SECRET_KEY` (cualquier clave, p. ej. `clave_final_2026`).
7. **Actions → Pipeline Despliegue Continuo (CD) → Run workflow** tres veces, con `caido`, `exitoso`
   y `fallo`. Llegan 3 alertas: servidor inaccesible, despliegue exitoso y rollback automático.
8. Desde el PC, **reemplazando** los valores de ejemplo por los reales (sin `< >`):

   ```powershell
   $env:TELEGRAM_BOT_TOKEN = "1234567890:AAEj_token_completo"
   $env:TELEGRAM_CHAT_ID = "6690192311"
   python scripts/run_deploy.py --escenario exitoso
   ```

| Mensaje en consola | Causa |
|---|---|
| `Notificación enviada a Telegram` | Todo correcto |
| `Telegram no configurado` | Faltan las variables o el nombre del secret está mal escrito |
| `HTTP 404` | Token mal copiado o incompleto |
| `HTTP 401` | Token revocado: genera otro con `/token` en @BotFather |
| `HTTP 400` | Chat ID incorrecto o no se pulsó **Iniciar** en el bot |
| `HTTP 403` | El bot está bloqueado en Telegram |

Si el token llega a quedar expuesto: en @BotFather → `/revoke` → elige el bot → actualiza el secreto.

### Semana 10: Infraestructura como Código

```powershell
docker compose --profile iac up -d localstack     # nube AWS emulada en el puerto 4566
docker ps                                         # localstack_lab10 en estado Up
python -m src.semana10.init_infra                 # crea mi-bucket-pruebas y cola-notificaciones
python -m src.semana10.init_infra                 # idempotente: mismo resultado ("existente")
docker compose --profile iac down                 # destruye la nube sin dejar rastros
```

Con LocalStack arriba, las 2 pruebas de integración de `tests/semana10` dejan de omitirse y hacen un viaje
completo por S3 (subir/leer un objeto) y SQS (enviar/recibir un mensaje). Se omitió `version: '3.8'` del
manifiesto porque Docker Compose v2 lo marca como obsoleto.

## Quality Gate

El build se aprueba solo si se cumplen las tres condiciones:

1. **0 pruebas fallidas**
2. **Cobertura ≥ 80%** sobre `src/` (líneas + ramas)
3. **0 hallazgos de flake8** (análisis estático)

La prueba de carga tiene su propio veredicto: 0 peticiones fallidas, p95 de `/fast` < 500 ms y p95 de `/slow` < 1500 ms.
El despliegue tiene el suyo: el Smoke Test en Staging debe responder HTTP 200.

## Inyección de fallas (para la sustentación)

| Clase | Cambio | Qué se pone rojo |
|---|---|---|
| 1 | `edad >= 18` → `edad > 18` en `sistema.py` | `test_acceso_exactamente_18` |
| 2 | `ingresos >= 2000.0` → `ingresos > 2000.0` | `test_evaluar_prestamo_fronteras[700-2000.0-APROBADO]` |
| 3 | ejecutar solo `-m semana1` | cobertura ~20% → Quality Gate rechazado |
| 4 | descuento del estudiante `50.0` → `40.0` en `app.py` ("Break the Container") | `test_descuento_estudiante_alta_cobertura`, exit code 1 |
| 5 | `"active": True` → `"active": "SI"` en `main.py` | `test_get_users_schema_validation` |
| 6 | cualquiera de los anteriores + `git push` | el pipeline de GitHub Actions se pone rojo y el CD no se dispara |
| 7 | agregar a `calculadora.py` una variable sin uso (`descuento_fantasma = 0.10`) | flake8 `F841` → Quality Gate rechazado |
| 8 | subir `RETARDO_SLOW_SEGUNDOS` a `2` en `semana8/api.py` | prueba de carga: p95 de `/slow` supera el umbral |
| 9 | `IS_HEALTHY = False` en `semana9/main.py` | Smoke Test HTTP 500 → rollback automático y alerta en Telegram |
| 10 | apagar LocalStack (`docker compose --profile iac down`) | el dashboard muestra "LocalStack no disponible" y las pruebas de integración se omiten |

Después de cada cambio, pulsa **Ejecutar pruebas**, **Lanzar enjambre** o **Ejecutar pipeline CD** en el
dashboard y verás el fallo con su mensaje. Recuerda deshacer el cambio al terminar.
