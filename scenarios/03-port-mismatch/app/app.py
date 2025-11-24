#!/usr/bin/env python3
"""
Kubernetes Masterclass - Scenario 3: Port Mismatch
A simple Flask web application for testing service port configuration.
"""

from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Welcome to the Kubernetes Masterclass!",
        "scenario": "03 - Port Mismatch",
        "timestamp": datetime.now().isoformat(),
        "pod_name": os.getenv('HOSTNAME', 'unknown')
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting web application on port {port}...")
    app.run(host='0.0.0.0', port=port)
