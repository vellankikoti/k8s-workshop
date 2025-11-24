#!/usr/bin/env python3
"""
File Upload Service - Demonstrates PersistentVolumeClaim usage
Allows file uploads and stores them on persistent storage
"""
from flask import Flask, render_template_string, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json

app = Flask(__name__)

UPLOAD_FOLDER = '/data/uploads'
METADATA_FILE = '/data/metadata.json'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_metadata():
    """Load file metadata"""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    """Save file metadata"""
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

UPLOAD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>File Upload Service</title>
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
        .upload-box {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .file-input {
            padding: 15px;
            border: 2px dashed #667eea;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .file-input:hover {
            background: #f8f9fa;
            border-color: #764ba2;
        }
        .upload-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 5px;
            font-size: 1.1em;
            cursor: pointer;
            margin-top: 15px;
        }
        .upload-btn:hover {
            opacity: 0.9;
        }
        .file-list {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .file-item {
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .file-name {
            font-weight: bold;
            color: #333;
        }
        .file-meta {
            font-size: 0.9em;
            color: #666;
        }
        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .storage-info {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📁 File Upload Service</h1>
        <p>Upload and manage your files on persistent storage</p>
        <p style="font-size: 0.9em; opacity: 0.8;">Pod: {{ pod_name }}</p>
    </div>

    <div class="upload-box">
        <h2>Upload File</h2>
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="file-input">
                <input type="file" id="fileInput" name="file" style="display:none" onchange="showFileName()">
                <label for="fileInput" style="cursor:pointer">
                    <p id="fileLabel">📎 Click to select file</p>
                    <p style="font-size:0.9em; color:#666">Allowed: txt, pdf, images, doc</p>
                </label>
            </div>
            <button type="submit" class="upload-btn">Upload File</button>
        </form>
        <div id="message"></div>
    </div>

    <div class="file-list">
        <h2>Uploaded Files ({{ file_count }})</h2>
        {% if files %}
        {% for filename, meta in files.items() %}
        <div class="file-item">
            <div>
                <div class="file-name">📄 {{ filename }}</div>
                <div class="file-meta">
                    Uploaded: {{ meta.uploaded_at }} | Size: {{ "%.2f"|format(meta.size_kb) }} KB
                </div>
            </div>
        </div>
        {% endfor %}
        {% else %}
        <p style="text-align:center; color:#666">No files uploaded yet</p>
        {% endif %}
    </div>

    <div class="storage-info">
        <strong>💾 Persistent Storage:</strong> All files are stored on a PersistentVolume.<br>
        Files will persist even if the pod is restarted or rescheduled.
    </div>

    <script>
        function showFileName() {
            const input = document.getElementById('fileInput');
            const label = document.getElementById('fileLabel');
            if (input.files.length > 0) {
                label.textContent = '✅ ' + input.files[0].name;
            }
        }

        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData();
            const fileInput = document.getElementById('fileInput');

            if (fileInput.files.length === 0) {
                document.getElementById('message').innerHTML =
                    '<div class="error">Please select a file</div>';
                return;
            }

            formData.append('file', fileInput.files[0]);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('message').innerHTML =
                        '<div class="success">✅ File uploaded successfully!</div>';
                    setTimeout(() => location.reload(), 1500);
                } else {
                    document.getElementById('message').innerHTML =
                        '<div class="error">❌ ' + data.message + '</div>';
                }
            })
            .catch(error => {
                document.getElementById('message').innerHTML =
                    '<div class="error">❌ Upload failed: ' + error + '</div>';
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    metadata = load_metadata()
    return render_template_string(
        UPLOAD_TEMPLATE,
        files=metadata,
        file_count=len(metadata),
        pod_name=os.getenv('HOSTNAME', 'unknown')
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload file to persistent storage"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Save file
        file.save(filepath)

        # Update metadata
        metadata = load_metadata()
        file_size = os.path.getsize(filepath)
        metadata[filename] = {
            'uploaded_at': datetime.now().isoformat(),
            'size_kb': file_size / 1024,
            'pod': os.getenv('HOSTNAME', 'unknown')
        }
        save_metadata(metadata)

        print(f"✅ File uploaded: {filename} ({file_size} bytes)")

        return jsonify({
            'success': True,
            'filename': filename,
            'size': file_size
        })
    else:
        return jsonify({
            'success': False,
            'message': 'File type not allowed'
        }), 400

@app.route('/files')
def list_files():
    """List all uploaded files"""
    metadata = load_metadata()
    return jsonify({
        'files': metadata,
        'count': len(metadata)
    })

@app.route('/health')
def health():
    # Check if storage is writable
    try:
        test_file = os.path.join(UPLOAD_FOLDER, '.health_check')
        with open(test_file, 'w') as f:
            f.write('ok')
        os.remove(test_file)
        storage_ok = True
    except:
        storage_ok = False

    return jsonify({
        'status': 'healthy' if storage_ok else 'degraded',
        'storage': 'writable' if storage_ok else 'not writable'
    })

if __name__ == '__main__':
    print("📁 Starting File Upload Service...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Pod: {os.getenv('HOSTNAME', 'unknown')}")
    app.run(host='0.0.0.0', port=5000)
