FROM python:3.11-alpine

# Metadata
LABEL org.opencontainers.image.source="https://github.com/vellankikoti/k8s-masterclass"
LABEL org.opencontainers.image.description="Kubernetes Masterclass - Scenario 3: Port Mismatch"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Install Flask
RUN pip install --no-cache-dir flask==3.0.0

COPY app.py .

ENV PORT=5000

EXPOSE 5000

CMD ["python3", "app.py"]
