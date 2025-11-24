FROM python:3.11-alpine

LABEL org.opencontainers.image.source="https://github.com/vellankikoti/k8s-workshop"
LABEL org.opencontainers.image.description="K8s Workshop - Scenario 8: Network Policy - Order Service"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

RUN pip install --no-cache-dir flask==3.0.0 requests==2.31.0

COPY app.py .

EXPOSE 5000

CMD ["python3", "app.py"]
