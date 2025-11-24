#!/usr/bin/env python3
"""
Simple Blog App - Demonstrates ConfigMap usage
Reads blog configuration from ConfigMap-mounted files
"""
from flask import Flask, render_template_string, jsonify
import os
import json

app = Flask(__name__)

# Read configuration from ConfigMap mount
CONFIG_PATH = '/config/blog.json'

def load_config():
    """Load blog configuration from ConfigMap"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            print(f"✅ Configuration loaded: {config}")
            return config
    except FileNotFoundError:
        print(f"❌ ERROR: Configuration file not found at {CONFIG_PATH}")
        print("Make sure the ConfigMap is mounted correctly!")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in configuration: {e}")
        raise

# Load config at startup
blog_config = load_config()

BLOG_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ blog_name }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .tagline {
            margin-top: 10px;
            font-size: 1.2em;
            opacity: 0.9;
        }
        .config-info {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .config-item {
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
        }
        .config-item strong {
            color: #667eea;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📝 {{ blog_name }}</h1>
        <p class="tagline">{{ tagline }}</p>
    </div>

    <div class="config-info">
        <h2>🔧 Blog Configuration</h2>
        <div class="config-item">
            <strong>Author:</strong> {{ author }}
        </div>
        <div class="config-item">
            <strong>Theme:</strong> {{ theme }}
        </div>
        <div class="config-item">
            <strong>Max Posts per Page:</strong> {{ max_posts }}
        </div>
        <div class="config-item">
            <strong>Comments Enabled:</strong> {{ comments_enabled }}
        </div>
    </div>

    <div class="footer">
        <p>Configuration loaded from Kubernetes ConfigMap ✅</p>
        <p>Pod: {{ pod_name }}</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(
        BLOG_TEMPLATE,
        blog_name=blog_config.get('blog_name', 'My Blog'),
        tagline=blog_config.get('tagline', 'Powered by Kubernetes'),
        author=blog_config.get('author', 'Unknown'),
        theme=blog_config.get('theme', 'default'),
        max_posts=blog_config.get('max_posts_per_page', 10),
        comments_enabled=blog_config.get('comments_enabled', False),
        pod_name=os.getenv('HOSTNAME', 'unknown')
    )

@app.route('/config')
def config():
    """Return current configuration as JSON"""
    return jsonify(blog_config)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'config_loaded': True})

if __name__ == '__main__':
    print("Starting Blog App...")
    print(f"Configuration: {blog_config}")
    app.run(host='0.0.0.0', port=5000)
