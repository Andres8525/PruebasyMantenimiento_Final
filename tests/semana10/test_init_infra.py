"""Semana 10 — Pruebas del aprovisionamiento IaC.

- Unitarias (siempre): clientes AWS falsos en memoria; validan creación e idempotencia.
- Integración (solo si LocalStack responde en LOCALSTACK_ENDPOINT o localhost:4566):
  aprovisionan de verdad y hacen un viaje completo por S3 y SQS.
"""

import socket
from urllib.parse import urlparse

import pytest
from botocore.exceptions import ClientError

from src.semana10 import init_infra


class FakeS3:
    def __init__(self):
        self.buckets = set()

    def list_buckets(self):
        return {"Buckets": [{"Name": n} for n in self.buckets]}

    def create_bucket(self, Bucket):
        self.buckets.add(Bucket)


class FakeSQS:
    def __init__(self, error_code="AWS.SimpleQueueService.NonExistentQueue"):
        self.colas = {}
        self.error_code = error_code

    def get_queue_url(self, QueueName):
        if QueueName not in self.colas:
            raise ClientError({"Error": {"Code": self.error_code}}, "GetQueueUrl")
        return {"QueueUrl": self.colas[QueueName]}

    def create_queue(self, QueueName):
        self.colas[QueueName] = f"http://localhost:4566/000000000000/{QueueName}"
        return {"QueueUrl": self.colas[QueueName]}

    def list_queues(self):
        return {"QueueUrls": list(self.colas.values())}


# --- Unitarias ---
def test_aprovisiona_bucket_y_cola():
    s3, sqs = FakeS3(), FakeSQS()
    resultado = init_infra.aprovisionar(s3, sqs)
    assert resultado["bucket"] == "creado"
    assert resultado["cola"] == "creada"
    assert init_infra.inventario(s3, sqs) == {"buckets": [init_infra.BUCKET], "colas": [init_infra.COLA]}


def test_idempotencia_ejecutar_dos_veces_da_el_mismo_estado():
    s3, sqs = FakeS3(), FakeSQS()
    init_infra.aprovisionar(s3, sqs)
    estado_1 = init_infra.inventario(s3, sqs)
    segunda = init_infra.aprovisionar(s3, sqs)
    assert segunda["bucket"] == "existente"
    assert segunda["cola"] == "existente"
    assert init_infra.inventario(s3, sqs) == estado_1


def test_error_inesperado_de_sqs_no_se_oculta():
    with pytest.raises(ClientError):
        init_infra.asegurar_cola(FakeSQS(error_code="AccessDenied"))


def test_main_sin_localstack_devuelve_1(monkeypatch):
    class SinConexion:
        def list_buckets(self):
            raise ClientError({"Error": {"Code": "ServiceUnavailable"}}, "ListBuckets")

    monkeypatch.setattr(init_infra, "crear_cliente", lambda servicio: SinConexion())
    assert init_infra.main() == 1


def test_main_con_infra_devuelve_0(monkeypatch):
    clientes = {"s3": FakeS3(), "sqs": FakeSQS()}
    monkeypatch.setattr(init_infra, "crear_cliente", lambda servicio: clientes[servicio])
    assert init_infra.main() == 0


# --- Integración contra LocalStack real ---
def _localstack_disponible() -> bool:
    destino = urlparse(init_infra.LOCALSTACK_ENDPOINT)
    try:
        with socket.create_connection((destino.hostname, destino.port or 4566), timeout=0.5):
            return True
    except OSError:
        return False


localstack = pytest.mark.skipif(not _localstack_disponible(), reason="LocalStack no está corriendo")


@localstack
def test_localstack_aprovisiona_e_idempotente():
    s3, sqs = init_infra.crear_cliente("s3"), init_infra.crear_cliente("sqs")
    init_infra.aprovisionar(s3, sqs)
    init_infra.aprovisionar(s3, sqs)
    estado = init_infra.inventario(s3, sqs)
    assert estado["buckets"].count(init_infra.BUCKET) == 1
    assert estado["colas"].count(init_infra.COLA) == 1


@localstack
def test_localstack_expediente_en_s3_y_decision_en_sqs():
    s3, sqs = init_infra.crear_cliente("s3"), init_infra.crear_cliente("sqs")
    _, url_cola = init_infra.asegurar_cola(sqs)
    init_infra.asegurar_bucket(s3)

    clave, expediente = "solicitudes/SOL-0001.json", b'{"score": 720, "decision": "APROBADO"}'
    s3.put_object(Bucket=init_infra.BUCKET, Key=clave, Body=expediente)
    assert s3.get_object(Bucket=init_infra.BUCKET, Key=clave)["Body"].read() == expediente

    sqs.send_message(QueueUrl=url_cola, MessageBody="SOL-0001:APROBADO")
    mensajes = sqs.receive_message(QueueUrl=url_cola, WaitTimeSeconds=1).get("Messages", [])
    assert [m["Body"] for m in mensajes] == ["SOL-0001:APROBADO"]
    sqs.delete_message(QueueUrl=url_cola, ReceiptHandle=mensajes[0]["ReceiptHandle"])
