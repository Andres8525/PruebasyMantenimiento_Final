"""Caso de uso: Banca — catálogo de casos de uso del sistema de crédito.

Cada caso de uso apunta a la semana (componente) que lo implementa y a su evidencia.
"fuente" indica de dónde sale su estado en el dashboard:
    semanaN -> resultado de las pruebas de esa semana
    banca   -> resultado de las pruebas de tests/banca
    gate    -> resultado del gate de reglas en el último despliegue
"""

CASOS_DE_USO = [
    {"id": "CU-01", "nombre": "Verificar la mayoría de edad del solicitante", "actor": "Canal digital",
     "semana": "1", "fuente": "semana1", "evidencia": "src/semana1/solicitante.py"},
    {"id": "CU-02", "nombre": "Evaluar score, ingresos, edad financiable y nivel de riesgo",
     "actor": "Analista de crédito", "semana": "2", "fuente": "semana2",
     "evidencia": "src/semana2/ (validador, edad, riesgo)"},
    {"id": "CU-03", "nombre": "Clasificar el perfil del cliente", "actor": "Analista de crédito",
     "semana": "3", "fuente": "semana3", "evidencia": "src/semana3/perfil_cliente.py"},
    {"id": "CU-04", "nombre": "Calcular el descuento sobre la tasa de interés", "actor": "Motor de tasas",
     "semana": "4", "fuente": "semana4", "evidencia": "src/semana4/tasa_interes.py (contenedor qa-runner)"},
    {"id": "CU-05", "nombre": "Consultar los clientes del banco", "actor": "Asesor comercial",
     "semana": "5", "fuente": "semana5", "evidencia": "GET /api/v1/clientes (JSON Schema)"},
    {"id": "CU-06", "nombre": "Integrar cambios del servicio de crédito", "actor": "Desarrollador",
     "semana": "6", "fuente": "semana6", "evidencia": ".github/workflows/ci.yml"},
    {"id": "CU-07", "nombre": "Calcular el total a pagar con código limpio", "actor": "Motor de tasas",
     "semana": "7", "fuente": "semana7", "evidencia": "src/semana7/total_credito.py + flake8 + SonarCloud"},
    {"id": "CU-08", "nombre": "Atender consultas masivas de simulación y buró", "actor": "Clientes concurrentes",
     "semana": "8", "fuente": "semana8", "evidencia": "load/locustfile.py"},
    {"id": "CU-09", "nombre": "Desplegar el servicio de crédito con rollback automático",
     "actor": "Pipeline de CD", "semana": "9", "fuente": "semana9", "evidencia": ".github/workflows/cd.yml"},
    {"id": "CU-10", "nombre": "Guardar expedientes y publicar decisiones de crédito",
     "actor": "Servicio de crédito", "semana": "10", "fuente": "semana10",
     "evidencia": "S3 banco-solicitudes-credito + SQS cola-decisiones-credito"},
    {"id": "CU-11", "nombre": "Evaluar una solicitud de crédito completa", "actor": "Cliente / canal digital",
     "semana": "1-7", "fuente": "banca", "evidencia": "POST /api/v1/creditos/solicitudes"},
    {"id": "CU-12", "nombre": "Bloquear cambios que rompen la regla de aprobación y notificar",
     "actor": "Pipeline de CD -> On-call", "semana": "2 y 9", "fuente": "gate",
     "evidencia": "Gate de reglas en scripts/run_deploy.py + Telegram"},
]
