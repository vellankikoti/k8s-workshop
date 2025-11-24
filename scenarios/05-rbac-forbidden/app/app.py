#!/usr/bin/env python3
"""
Pod Monitor Dashboard - Demonstrates RBAC usage
Lists pods in the namespace using Kubernetes API
Requires proper ServiceAccount with RBAC permissions
"""
from flask import Flask, render_template_string, jsonify
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os

app = Flask(__name__)

# Load in-cluster Kubernetes config
try:
    config.load_incluster_config()
    print("✅ Loaded in-cluster Kubernetes config")
except:
    print("⚠️  Not running in cluster, trying local config")
    config.load_kube_config()

v1 = client.CoreV1Api()
NAMESPACE = os.getenv('NAMESPACE', 'default')

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pod Monitor Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="5">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        h1 {
            margin: 0;
            font-size: 2em;
        }
        .subtitle {
            margin-top: 10px;
            opacity: 0.9;
        }
        .pod-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .pod-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .pod-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .pod-status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .status-running {
            background: #d4edda;
            color: #155724;
        }
        .status-pending {
            background: #fff3cd;
            color: #856404;
        }
        .status-failed {
            background: #f8d7da;
            color: #721c24;
        }
        .pod-info {
            font-size: 0.9em;
            color: #666;
            line-height: 1.8;
        }
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #f5c6cb;
        }
        .error-message h2 {
            margin-top: 0;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Pod Monitor Dashboard</h1>
        <p class="subtitle">Real-time Pod Status | Namespace: {{ namespace }}</p>
    </div>

    {% if error %}
    <div class="error-message">
        <h2>❌ Permission Denied</h2>
        <p><strong>Error:</strong> {{ error }}</p>
        <p>This application needs permission to list pods in the namespace.</p>
        <p><strong>Check:</strong> ServiceAccount, Role, and RoleBinding configuration</p>
    </div>
    {% else %}
    <div class="pod-grid">
        {% for pod in pods %}
        <div class="pod-card">
            <div class="pod-name">{{ pod.name }}</div>
            <div class="pod-status status-{{ pod.status|lower }}">
                {{ pod.status }}
            </div>
            <div class="pod-info">
                <div>📦 <strong>Ready:</strong> {{ pod.ready }}</div>
                <div>🔄 <strong>Restarts:</strong> {{ pod.restarts }}</div>
                <div>⏱️  <strong>Age:</strong> {{ pod.age }}</div>
                <div>🏷️  <strong>Node:</strong> {{ pod.node }}</div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="footer">
        <p>Auto-refreshes every 5 seconds | Pod: {{ current_pod }}</p>
    </div>
</body>
</html>
"""

def get_pods():
    """Get list of pods in namespace"""
    try:
        pods = v1.list_namespaced_pod(namespace=NAMESPACE)
        pod_list = []

        for pod in pods.items:
            # Calculate age
            from datetime import datetime, timezone
            age_seconds = (datetime.now(timezone.utc) - pod.metadata.creation_timestamp).total_seconds()
            if age_seconds < 60:
                age = f"{int(age_seconds)}s"
            elif age_seconds < 3600:
                age = f"{int(age_seconds/60)}m"
            else:
                age = f"{int(age_seconds/3600)}h"

            # Get ready count
            ready_count = sum(1 for c in pod.status.container_statuses if c.ready) if pod.status.container_statuses else 0
            total_count = len(pod.spec.containers)

            # Get restart count
            restarts = sum(c.restart_count for c in pod.status.container_statuses) if pod.status.container_statuses else 0

            pod_list.append({
                'name': pod.metadata.name,
                'status': pod.status.phase,
                'ready': f"{ready_count}/{total_count}",
                'restarts': restarts,
                'age': age,
                'node': pod.spec.node_name or 'N/A'
            })

        return pod_list, None

    except ApiException as e:
        if e.status == 403:
            error_msg = "Forbidden: ServiceAccount lacks permission to list pods. Check RBAC configuration!"
        else:
            error_msg = f"API Error {e.status}: {e.reason}"
        print(f"❌ ERROR: {error_msg}")
        return [], error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ ERROR: {error_msg}")
        return [], error_msg

@app.route('/')
def index():
    pods, error = get_pods()
    return render_template_string(
        DASHBOARD_TEMPLATE,
        pods=pods,
        error=error,
        namespace=NAMESPACE,
        current_pod=os.getenv('HOSTNAME', 'unknown')
    )

@app.route('/api/pods')
def api_pods():
    """Return pods as JSON"""
    pods, error = get_pods()
    if error:
        return jsonify({'error': error}), 403
    return jsonify({'pods': pods, 'count': len(pods)})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("Starting Pod Monitor Dashboard...")
    print(f"Monitoring namespace: {NAMESPACE}")
    app.run(host='0.0.0.0', port=5000)
