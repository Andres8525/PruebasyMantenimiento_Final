# Imagen de QA: la usan el test-runner efímero y el dashboard.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pytest.ini .coveragerc ./
COPY config ./config
COPY src ./src
COPY tests ./tests
COPY scripts ./scripts
COPY dashboard ./dashboard

# Por defecto: ejecutar la suite completa y generar reportes
CMD ["python", "scripts/run_tests.py"]
