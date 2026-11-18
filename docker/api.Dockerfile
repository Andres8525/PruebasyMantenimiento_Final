# Imagen del microservicio objetivo (Semana 5). Contexto de build: raíz del proyecto.
FROM python:3.11-slim

# curl para el healthcheck de Docker Compose
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip install --no-cache-dir fastapi==0.125.0 uvicorn==0.46.0

COPY src/semana5/main.py .

EXPOSE 8000
# 0.0.0.0 para aceptar peticiones desde otros contenedores
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
