FROM python:3.11-alpine

# Metadata
LABEL org.opencontainers.image.source="https://github.com/vellankikoti/k8s-masterclass"
LABEL org.opencontainers.image.description="Kubernetes Masterclass - Scenario 1: CrashLoopBackOff"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

COPY app.py .

RUN chmod +x app.py

CMD ["python3", "app.py"]
