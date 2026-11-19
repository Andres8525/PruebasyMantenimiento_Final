"""Semana 10 — Aprovisionamiento IaC en LocalStack (AWS emulado en Docker).

Componente del sistema de crédito: almacenamiento de solicitudes y cola de decisiones.
Crea el bucket S3 'banco-solicitudes-credito' (expedientes de cada solicitud) y la
cola SQS 'cola-decisiones-credito' (decisiones que consumen los demás sistemas del banco).
Es idempotente: ejecutarlo 1 o 100 veces deja exactamente el mismo estado.

Uso:
    docker compose --profile iac up -d localstack
    python -m src.semana10.init_infra
"""

from __future__ import annotations

import os
import sys

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")
REGION = "us-east-1"
BUCKET = "banco-solicitudes-credito"
COLA = "cola-decisiones-credito"

_COLA_INEXISTENTE = {"AWS.SimpleQueueService.NonExistentQueue", "QueueDoesNotExist"}


def crear_cliente(servicio: str, endpoint: str | None = None):
    """Cliente boto3 con credenciales dummy: LocalStack no valida credenciales reales."""
    return boto3.client(
        servicio,
        endpoint_url=endpoint or LOCALSTACK_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name=REGION,
        config=Config(connect_timeout=2, read_timeout=5, retries={"max_attempts": 1}),
    )


def asegurar_bucket(s3, nombre: str = BUCKET) -> str:
    existentes = {b["Name"] for b in s3.list_buckets().get("Buckets", [])}
    if nombre in existentes:
        return "existente"
    s3.create_bucket(Bucket=nombre)
    return "creado"


def asegurar_cola(sqs, nombre: str = COLA) -> tuple[str, str]:
    try:
        return "existente", sqs.get_queue_url(QueueName=nombre)["QueueUrl"]
    except ClientError as error:
        if error.response["Error"]["Code"] not in _COLA_INEXISTENTE:
            raise
    return "creada", sqs.create_queue(QueueName=nombre)["QueueUrl"]


def inventario(s3, sqs) -> dict:
    """Estado actual de la nube local (para auditar y para el dashboard)."""
    return {
        "buckets": sorted(b["Name"] for b in s3.list_buckets().get("Buckets", [])),
        "colas": sorted(u.rsplit("/", 1)[-1] for u in sqs.list_queues().get("QueueUrls", [])),
    }


def aprovisionar(s3, sqs) -> dict:
    print("=== APROVISIONANDO INFRAESTRUCTURA IAC EN LOCALSTACK ===")
    estado_bucket = asegurar_bucket(s3)
    print(f" -> [OK] Bucket S3 '{BUCKET}' {estado_bucket}.")
    estado_cola, url_cola = asegurar_cola(sqs)
    print(f" -> [OK] Cola SQS '{COLA}' {estado_cola}.")
    print("[ÉXITO] Infraestructura lista para su uso.")
    return {"bucket": estado_bucket, "cola": estado_cola, "url_cola": url_cola}


def main() -> int:
    try:
        aprovisionar(crear_cliente("s3"), crear_cliente("sqs"))
    except (BotoCoreError, ClientError) as error:
        print(f" -> [ERROR] No se pudo aprovisionar en {LOCALSTACK_ENDPOINT}: {type(error).__name__}")
        print("    ¿Está LocalStack arriba?  docker compose --profile iac up -d localstack")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
