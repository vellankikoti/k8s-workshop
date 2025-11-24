#!/usr/bin/env python3
"""
Image Processor - Demonstrates memory limits and OOMKilled
Processes images in memory, needs appropriate memory limits
"""
from flask import Flask, render_template_string, request, jsonify
from PIL import Image, ImageFilter
import io
import base64
import os

app = Flask(__name__)

# Simulated image processing that uses memory
PROCESSED_IMAGES = []

IMAGE_PROCESSOR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Image Processor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
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
        }
        .processor {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 5px;
            font-size: 1.1em;
            cursor: pointer;
            margin: 10px 5px;
        }
        .button:hover {
            opacity: 0.9;
        }
        .stats {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .stat-item {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
        }
        .warning {
            background: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #ffc107;
            margin-top: 20px;
        }
        .memory-bar {
            background: #e9ecef;
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }
        .memory-fill {
            background: linear-gradient(90deg, #28a745 0%, #ffc107 50%, #dc3545 100%);
            height: 100%;
            transition: width 0.5s;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🖼️ Image Processor Service</h1>
        <p>Simulated Image Processing with Memory Usage</p>
    </div>

    <div class="processor">
        <h2>Process Images</h2>
        <p>Click below to simulate image processing (uses memory)</p>

        <button class="button" onclick="processImage(1)">Process 1 Image (10MB)</button>
        <button class="button" onclick="processImage(5)">Process 5 Images (50MB)</button>
        <button class="button" onclick="processImage(10)">Process 10 Images (100MB)</button>

        <div class="stats">
            <h3>📊 Processing Statistics</h3>
            <div class="stat-item">
                <span>Images Processed:</span>
                <span id="processed-count">{{ processed_count }}</span>
            </div>
            <div class="stat-item">
                <span>Memory Used (approx):</span>
                <span id="memory-used">{{ memory_used }} MB</span>
            </div>
        </div>

        <div class="memory-bar">
            <div class="memory-fill" id="memory-bar" style="width: {{ memory_percent }}%"></div>
        </div>

        <div class="warning">
            <strong>⚠️ Memory Limit Warning:</strong><br>
            This pod has limited memory. Processing too many images at once may cause an OOMKilled error!
        </div>
    </div>

    <script>
        function processImage(count) {
            fetch('/process', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({count: count})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('processed-count').textContent = data.total_processed;
                document.getElementById('memory-used').textContent = data.memory_used_mb;

                const percent = Math.min((data.memory_used_mb / 256) * 100, 100);
                document.getElementById('memory-bar').style.width = percent + '%';

                if (data.warning) {
                    alert('⚠️ ' + data.warning);
                }
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        }

        // Auto-refresh stats every 3 seconds
        setInterval(() => {
            fetch('/stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('processed-count').textContent = data.total_processed;
                document.getElementById('memory-used').textContent = data.memory_used_mb;
            });
        }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    memory_used_mb = len(PROCESSED_IMAGES) * 10
    memory_percent = min((memory_used_mb / 256) * 100, 100)

    return render_template_string(
        IMAGE_PROCESSOR_TEMPLATE,
        processed_count=len(PROCESSED_IMAGES),
        memory_used=memory_used_mb,
        memory_percent=memory_percent
    )

@app.route('/process', methods=['POST'])
def process():
    """Simulate image processing by allocating memory"""
    data = request.get_json()
    count = data.get('count', 1)

    # Simulate processing by creating large data structures
    for i in range(count):
        # Allocate ~10MB per "image"
        dummy_data = bytearray(10 * 1024 * 1024)  # 10MB
        PROCESSED_IMAGES.append(dummy_data)

    memory_used_mb = len(PROCESSED_IMAGES) * 10

    warning = None
    if memory_used_mb > 200:
        warning = f"Memory usage is {memory_used_mb}MB! OOMKilled may occur if limit is too low!"

    print(f"Processed {count} images. Total: {len(PROCESSED_IMAGES)} images ({memory_used_mb}MB)")

    return jsonify({
        'total_processed': len(PROCESSED_IMAGES),
        'memory_used_mb': memory_used_mb,
        'warning': warning
    })

@app.route('/stats')
def stats():
    """Return current stats"""
    memory_used_mb = len(PROCESSED_IMAGES) * 10
    return jsonify({
        'total_processed': len(PROCESSED_IMAGES),
        'memory_used_mb': memory_used_mb
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'processed': len(PROCESSED_IMAGES)})

if __name__ == '__main__':
    print("Starting Image Processor...")
    app.run(host='0.0.0.0', port=5000)
