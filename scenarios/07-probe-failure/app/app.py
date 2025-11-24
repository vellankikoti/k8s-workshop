#!/usr/bin/env python3
"""
API Service with Health Checks - Demonstrates liveness and readiness probes
Has /health (liveness) and /ready (readiness) endpoints
"""
from flask import Flask, jsonify
import time
import os

app = Flask(__name__)

# Startup time simulation
START_TIME = time.time()
STARTUP_DELAY = 10  # seconds to become ready

# Simulated health state
healthy = True
ready = False

@app.route('/')
def index():
    return jsonify({
        'service': 'API Health Demo',
        'status': 'running',
        'healthy': healthy,
        'ready': ready,
        'uptime': int(time.time() - START_TIME),
        'pod': os.getenv('HOSTNAME', 'unknown')
    })

@app.route('/ready')
def readiness():
    """Readiness probe endpoint - checks if app can handle traffic"""
    global ready

    # Simulate startup time
    uptime = time.time() - START_TIME
    if uptime > STARTUP_DELAY:
        ready = True

    if ready:
        return jsonify({
            'status': 'ready',
            'message': 'Application is ready to receive traffic',
            'uptime': int(uptime)
        }), 200
    else:
        return jsonify({
            'status': 'not ready',
            'message': f'Application is starting up... ({int(STARTUP_DELAY - uptime)}s remaining)',
            'uptime': int(uptime)
        }), 503

@app.route('/health')
def liveness():
    """Liveness probe endpoint - checks if app is alive"""
    if healthy:
        return jsonify({
            'status': 'healthy',
            'message': 'Application is running normally'
        }), 200
    else:
        return jsonify({
            'status': 'unhealthy',
            'message': 'Application has encountered a fatal error'
        }), 500

@app.route('/api/data')
def get_data():
    """Sample API endpoint"""
    if not ready:
        return jsonify({'error': 'Service not ready'}), 503

    return jsonify({
        'data': [
            {'id': 1, 'name': 'Kubernetes'},
            {'id': 2, 'name': 'Docker'},
            {'id': 3, 'name': 'DevOps'}
        ],
        'timestamp': time.time()
    })

@app.route('/kill')
def kill():
    """Simulate unhealthy state (for testing)"""
    global healthy
    healthy = False
    return jsonify({'message': 'Application marked as unhealthy'})

if __name__ == '__main__':
    print("Starting API Service...")
    print(f"Startup delay: {STARTUP_DELAY} seconds")
    print("Endpoints:")
    print("  /health - Liveness probe")
    print("  /ready - Readiness probe")
    print("  /api/data - Sample API")
    app.run(host='0.0.0.0', port=5000)
