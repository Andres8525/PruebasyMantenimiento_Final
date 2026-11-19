# Sistema de Crédito Bancario — Proyecto Final de Pruebas y Mantenimiento de Software (DevOps)

Universidad Cooperativa de Colombia · Docente: Mg. Gabriel Guerrero Arellano

**Equipo:** Diego (Semanas 1–3) · Jhoan (Semanas 4–6) · Edison (Semanas 7–10)

Todo el proyecto es **un solo sistema: la evaluación automática de solicitudes de crédito de un banco**.
Cada semana del curso construyó y probó uno de sus componentes, y el flujo DevOps (contenedores,
integración continua, análisis estático, pruebas de carga, despliegue continuo e infraestructura como
código) garantiza que ningún cambio defectuoso llegue a producción.

**Garantía del sistema:** ningún cambio en las reglas de aprobación llega a Producción sin pasar las
pruebas de valores límite.

Estado actual: **139 pruebas**, cobertura **~98%**, **0 hallazgos** de flake8, 12 casos de uso verificados
y los pipelines de CI/CD en verde.

## Inicio rápido

```powershell
python -m pip install -r requirements.txt            # solo la primera vez
python scripts/run_tests.py                          # pruebas + linter + Quality Gate + reportes
python -m uvicorn dashboard.app:app --port 8090      # dashboard en http://localhost:8090
```

> Si aparece `[Errno 13] ... no permitido por sus permisos de acceso`, el puerto está ocupado: usa otro
> número, por ejemplo `--port 8095`.

Opcional, antes de arrancar el dashboard en la misma terminal:

```powershell
docker compose --profile iac up -d localstack        # Semana 10: S3 y SQS del banco (Docker Desktop abierto)
$env:TELEGRAM_BOT_TOKEN = "token_real_del_bot"       # Semana 9: alertas al celular
$env:TELEGRAM_CHAT_ID = "id_numerico_real"
```

Desde cero (otro computador):

```powershell
git clone https://github.com/Andres8525/PruebasyMantenimiento_Final.git
cd PruebasyMantenimiento_Final
python -m venv venv
.\venv\Scripts\activate          # si falla: Set-ExecutionPolicy -Scope Process Bypass
python -m pip install -r requirements.txt
python scripts/run_tests.py
python -m uvicorn dashboard.app:app --port 8090
```

## Cómo funciona el sistema

Una solicitud de crédito (`POST /api/v1/creditos/solicitudes`) recorre los componentes de cada semana y
solo se aprueba si todos la aceptan:

| Paso | Semana | Componente | Regla |
|---|---|---|---|
| 1 | 1 | Verificación del solicitante | 18 años o más |
| 2 | 2 | Edad financiable | entre 18 y 65 años |
| 3 | 2 | Nivel de riesgo | score 300–579 alto, 580–699 medio, 700–850 bajo (define la tasa base) |
| 4 | 2 | Regla de aprobación | score de al menos 600 **y** ingresos de al menos 2,000.00 |
| 5 | 3 | Perfil del cliente | cuenta activa; menor con perfil preferencial requiere codeudor |
| 6 | 4 | Descuento sobre la tasa | 50% con nómina y 80% de puntualidad; 30% con 90% de puntualidad |
| 7 | 7 | Total a pagar | monto + monto × tasa final |

El resto de semanas sostienen el sistema: la API de clientes (5), el servicio base e integración continua
(6), la simulación y la consulta al buró bajo carga (8), el despliegue con rollback (9) y el almacenamiento
de expedientes y decisiones en la nube (10).

## Componentes por semana

| Semana | Técnica del curso | Componente del sistema de crédito | Código | Pruebas |
|---|---|---|---|---|
| 1 | Patrón AAA, Pytest | Verificación del solicitante | `src/semana1/solicitante.py` | `tests/semana1/` |
| 2 | Partición de Equivalencia, BVA, `parametrize`, `pytest.raises` | Regla de aprobación, edad financiable y nivel de riesgo | `src/semana2/validador_credito.py`, `edad_credito.py`, `riesgo.py` | `tests/semana2/` |
| 3 | Cobertura y Quality Gate (`--cov-fail-under=80`) | Perfil del cliente (5 ramas) | `src/semana3/perfil_cliente.py` | `tests/semana3/` |
| 4 | Docker: imagen `qa-runner`, contenedor efímero | Descuento sobre la tasa de interés | `src/semana4/tasa_interes.py` | `tests/semana4/`, `docker/qa.Dockerfile` |
| 5 | API en contenedores (Requests + JSON Schema) | API de clientes del banco | `src/semana5/main.py` | `tests/semana5/`, `docker-compose.yml` |
| 6 | Integración Continua con GitHub Actions | Servicio de crédito base | `src/semana6/main.py` | `tests/semana6/`, `.github/workflows/ci.yml` |
| 7 | Análisis estático: flake8 + SonarCloud | Cálculo del total a pagar | `src/semana7/total_credito.py` | `tests/semana7/`, `.flake8`, `sonar.yml` |
| 8 | Pruebas de carga con Locust | Simulación de crédito y consulta al buró | `src/semana8/api.py`, `load/locustfile.py` | `tests/semana8/` |
| 9 | Despliegue Continuo, rollback, secrets, Telegram | Despliegue del servicio de crédito | `src/semana9/main.py`, `deploy.py` | `tests/semana9/`, `.github/workflows/cd.yml` |
| 10 | Infraestructura como Código con LocalStack | Expedientes (S3) y cola de decisiones (SQS) | `src/semana10/init_infra.py` | `tests/semana10/` |
| Sistema | Integración de todo lo anterior | Solicitud completa, política, matriz de valores límite y API | `src/banca/` | `tests/banca/` |

## Casos de uso

| ID | Caso de uso | Actor | Semana |
|---|---|---|---|
| CU-01 | Verificar la mayoría de edad del solicitante | Canal digital | 1 |
| CU-02 | Evaluar score, ingresos, edad financiable y nivel de riesgo | Analista de crédito | 2 |
| CU-03 | Clasificar el perfil del cliente | Analista de crédito | 3 |
| CU-04 | Calcular el descuento sobre la tasa de interés | Motor de tasas | 4 |
| CU-05 | Consultar los clientes del banco | Asesor comercial | 5 |
| CU-06 | Integrar cambios del servicio de crédito | Desarrollador | 6 |
| CU-07 | Calcular el total a pagar con código limpio | Motor de tasas | 7 |
| CU-08 | Atender consultas masivas de simulación y buró | Clientes concurrentes | 8 |
| CU-09 | Desplegar el servicio de crédito con rollback automático | Pipeline de CD | 9 |
| CU-10 | Guardar expedientes y publicar decisiones de crédito | Servicio de crédito | 10 |
| CU-11 | Evaluar una solicitud de crédito completa | Cliente / canal digital | 1–7 |
| CU-12 | Bloquear cambios que rompen la regla de aprobación y notificar | Pipeline de CD → On-call | 2 y 9 |

El catálogo está en `src/banca/casos_de_uso.py` y el dashboard muestra el estado de cada uno según las
pruebas de su semana.

## Cómo se protege la regla de aprobación

1. **Matriz de valores límite** (`src/banca/politica.py`, casos B01 a B12): cada borde se prueba en el
   límite (On point) y justo al lado (Off point): 599/600 de score, 1,999.99/2,000.00 de ingresos, los
   bordes del dominio y las entradas inválidas.
2. **CI**: la matriz forma parte de la suite, así que un borde roto pone el Quality Gate en rojo.
3. **Gate de reglas en el CD**: `scripts/run_deploy.py` vuelve a ejecutar la matriz **antes de Staging**.
   Si un caso falla, el despliegue queda *Bloqueado por reglas*, Producción sigue en la versión estable y
   llega la alerta a Telegram con los casos que fallaron.

## Estructura

```
Final_Devops/
├── src/semanaN/              # Componentes del sistema de crédito, uno por semana (1-10)
├── src/banca/                # Sistema integrado: solicitud completa, política, casos de uso y API
├── tests/semanaN/            # Pruebas de cada componente
├── tests/banca/              # Matriz de valores límite, solicitud completa y contrato de la API
├── load/locustfile.py        # Semana 8: clientes concurrentes (75% simulación, 25% buró)
├── dashboard/                # Dashboard de calidad (FastAPI + Jinja2)
├── scripts/
│   ├── run_tests.py          # pruebas + linter + Quality Gate + reportes
│   ├── run_load_test.py      # prueba de carga headless con Locust
│   └── run_deploy.py         # gate de reglas -> Staging -> promoción / rollback
├── docker/                   # api.Dockerfile · qa.Dockerfile (qa-runner)
├── docker-compose.yml        # api-service + test-runner + dashboard (+ perfiles "carga" e "iac")
├── .github/workflows/        # ci.yml · sonar.yml · cd.yml
└── reports/                  # salida generada (no se versiona)
```

## El dashboard

| Sección | Qué muestra |
|---|---|
| Resumen | Quality Gate con sus 3 condiciones, indicadores y el flujo DevOps con el estado de sus 8 etapas |
| El sistema | Regla del banco, garantía, **simulador de una solicitud completa** (veredicto de cada semana), los 12 casos de uso, cómo se protege la regla, mapa de bordes y matriz de valores límite |
| Semanas 1-3 (Diego) | Componentes de verificación, reglas y perfil; cobertura por módulo |
| Semanas 4-6 (Jhoan) | Descuento en contenedor, API de clientes, integración continua |
| Semanas 7-10 (Edison) | Total a pagar y análisis estático, carga, despliegue e infraestructura |
| Historial | Tendencia de éxito y cobertura entre ejecuciones |

Cada tarjeta de semana indica su **componente del sistema**, la técnica del curso, qué demuestra, cómo leer
el resultado, el comando para ejecutarla y sus pruebas.

## Comandos por semana

```powershell
python -m pytest -m semana2 -v --no-cov             # una semana (sin el gate de cobertura)
python -m pytest -m banca -v --no-cov               # sistema integrado y matriz de valores límite
python scripts/run_tests.py -m semana1              # demo de Quality Gate rechazado (cobertura ~34%)

docker build -f docker/qa.Dockerfile -t qa-runner:v1 .    # Semana 4: imagen inmutable
docker run --rm qa-runner:v1                              # contenedor efímero (exit code 0)
docker compose up --build --exit-code-from test-runner api-service test-runner   # Semana 5

python -m flake8 .                                  # Semana 7: análisis estático
python scripts/run_load_test.py -u 200 -r 20 -t 30  # Semana 8: carga headless
docker compose --profile carga up --build api-carga locust   # Semana 8: interfaz de Locust en :8089

python scripts/run_deploy.py --escenario exitoso    # Semana 9: gate + Staging 200 -> Producción
python scripts/run_deploy.py --escenario fallo      # Staging 500 -> rollback
python scripts/run_deploy.py --escenario caido      # Staging apagado -> rollback por conexión

docker compose --profile iac up -d localstack       # Semana 10: nube AWS emulada
python -m src.semana10.init_infra                   # crea banco-solicitudes-credito y cola-decisiones-credito
docker compose --profile iac down

python -m uvicorn src.banca.api:app --port 8002     # servicio de crédito solo (documentación en /docs)
```

## Integración y despliegue continuos

- **`ci.yml`** (cada push o pull request a `main`): pruebas y Quality Gate, contenedores, carga corta con
  Locust e infraestructura con LocalStack como servicio. Los reportes quedan como *artifacts*.
- **`sonar.yml`**: análisis en SonarCloud (requiere el secreto `SONAR_TOKEN`; sin él solo muestra un aviso).
  Las acciones están fijadas por SHA completo, la corrección que SonarCloud pide en la Semana 7.
- **`cd.yml`**: se ejecuta solo cuando el CI de `main` termina en verde. Corre el gate de reglas, el Smoke
  Test en Staging y promociona o revierte. También se lanza a mano desde **Actions → Run workflow**.

### Alertas a Telegram

El token del bot nunca va en el código: se lee de variables de entorno o de GitHub Secrets.

1. En Telegram, **@BotFather** → `/newbot` → nombre y usuario terminado en `bot` → copia el **token**.
2. Abre el enlace `t.me/...` de tu bot y pulsa **Iniciar**.
3. **@userinfobot** → **Iniciar** → copia tu **Id** (es el `TELEGRAM_CHAT_ID`).
4. En GitHub: **Settings → Secrets and variables → Actions** → crea `TELEGRAM_BOT_TOKEN`,
   `TELEGRAM_CHAT_ID` y `API_SECRET_KEY`.

| Mensaje en consola | Causa |
|---|---|
| `Notificación enviada a Telegram` | Todo correcto |
| `Telegram no configurado` | Faltan las variables o el nombre del secreto está mal escrito |
| `HTTP 404` | Token mal copiado o incompleto |
| `HTTP 401` | Token revocado: genera otro con `/token` en @BotFather |
| `HTTP 400` | Chat ID incorrecto o no se pulsó **Iniciar** en el bot |

## Quality Gate

La entrega se aprueba solo si cumple las tres condiciones:

1. **0 pruebas fallidas**
2. **Cobertura ≥ 80%** sobre `src/` (líneas + ramas)
3. **0 hallazgos de flake8**

La prueba de carga tiene su propio veredicto (0 fallos, p95 de la simulación < 500 ms y p95 del buró
< 1500 ms) y el despliegue el suyo (gate de reglas aprobado y Smoke Test HTTP 200).

## Inyección de fallas (para la sustentación)

| Semana | Cambio | Qué se pone rojo |
|---|---|---|
| 1 | `edad >= 18` → `edad > 18` en `src/semana1/solicitante.py` | `test_solicitante_exactamente_18` |
| 2 | `ingresos >= 2000.0` → `ingresos > 2000.0` en `src/semana2/validador_credito.py` | caso B08 de la matriz; el despliegue queda *Bloqueado por reglas* |
| 3 | ejecutar solo `-m semana1` | cobertura ~34% → Quality Gate rechazado |
| 4 | descuento `50.0` → `40.0` en `src/semana4/tasa_interes.py` | `test_descuento_cliente_nomina_puntual`, exit code 1 |
| 5 | `"activo": True` → `"activo": "SI"` en `src/semana5/main.py` | `test_clientes_schema_validation` |
| 6 | cualquiera de los anteriores + `git push` | el pipeline se pone rojo y el CD no se dispara |
| 7 | agregar `descuento_fantasma = 0.10` dentro de `calcular_total_credito` | flake8 `F841` → Quality Gate rechazado |
| 8 | subir `RETARDO_BURO_SEGUNDOS` a `2` en `src/semana8/api.py` | p95 del buró supera el umbral → carga rechazada |
| 9 | `IS_HEALTHY = False` en `src/semana9/main.py` | Smoke Test HTTP 500 → rollback y alerta en Telegram |
| 10 | apagar LocalStack | el dashboard muestra "LocalStack no disponible" y las pruebas de integración se omiten |

En el simulador de **El sistema** también se puede mostrar sin tocar código: el escenario
*Ingresos 1,999.99* rechaza la solicitud en la Semana 2 y *Ingresos 2,000.00* la aprueba.
Recuerda deshacer cada cambio al terminar.
