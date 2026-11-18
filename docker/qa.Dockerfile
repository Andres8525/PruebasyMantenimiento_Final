# Semana 4 — Imagen de QA inmutable ("qa-runner").
# La usan el test-runner efímero, el dashboard y Locust.
#   docker build -f docker/qa.Dockerfile -t qa-runner:v1 .
#   docker run --rm qa-runner:v1          -> exit code 0 = listo para CI/CD
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

# Dependencias primero para aprovechar la caché de capas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pytest.ini .coveragerc .flake8 ./
COPY config ./config
COPY src ./src
COPY tests ./tests
COPY scripts ./scripts
COPY dashboard ./dashboard
COPY load ./load

# Por defecto: suite completa + linter + Quality Gate
CMD ["python", "scripts/run_tests.py"]
