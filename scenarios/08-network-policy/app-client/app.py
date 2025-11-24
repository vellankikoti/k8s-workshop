#!/usr/bin/env python3
"""
Order Service - Frontend service for placing orders
Demonstrates NetworkPolicy - makes requests to inventory service
"""
from flask import Flask, render_template_string, jsonify, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Inventory service endpoint
INVENTORY_SERVICE = os.getenv('INVENTORY_SERVICE', 'inventory-service')
INVENTORY_URL = f'http://{INVENTORY_SERVICE}:80'

ORDER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Order Service</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px;
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
        .inventory-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .item-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .item-name {
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .price {
            color: #667eea;
            font-size: 1.4em;
            font-weight: bold;
            margin: 10px 0;
        }
        .stock {
            color: #28a745;
            font-weight: bold;
        }
        .order-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
        }
        .order-btn:hover {
            opacity: 0.9;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #f5c6cb;
            margin: 20px 0;
        }
        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .loading {
            text-align: center;
            padding: 40px;
            font-size: 1.2em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛒 Order Service</h1>
        <p>Place your orders here</p>
        <p style="font-size: 0.9em; opacity: 0.8;">Pod: {{ pod_name }}</p>
    </div>

    {% if error %}
    <div class="error">
        <h3>❌ Connection Error</h3>
        <p><strong>Cannot connect to Inventory Service!</strong></p>
        <p>Error: {{ error }}</p>
        <p>This might be a NetworkPolicy blocking traffic between services.</p>
        <p>Inventory Service: {{ inventory_url }}</p>
    </div>
    {% else %}
    <div class="inventory-grid">
        {% for key, item in inventory.items() %}
        <div class="item-card">
            <div class="item-name">{{ item.name }}</div>
            <div class="price">${{ "%.2f"|format(item.price) }}</div>
            <div class="stock">In Stock: {{ item.stock }}</div>
            <button class="order-btn" onclick="orderItem('{{ key }}')">Order Now</button>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div id="message"></div>

    <script>
        function orderItem(item) {
            fetch('/order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({item: item, quantity: 1})
            })
            .then(response => response.json())
            .then(data => {
                const msg = document.getElementById('message');
                if (data.success) {
                    msg.innerHTML = '<div class="success">✅ Order placed! Reserved: ' + data.reserved + '</div>';
                    setTimeout(() => location.reload(), 2000);
                } else {
                    msg.innerHTML = '<div class="error">❌ ' + data.message + '</div>';
                }
            })
            .catch(error => {
                document.getElementById('message').innerHTML =
                    '<div class="error">❌ Network error: ' + error + '</div>';
            });
        }
    </script>
</body>
</html>
"""

def fetch_inventory():
    """Fetch inventory from inventory service"""
    try:
        response = requests.get(f'{INVENTORY_URL}/inventory', timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get('inventory', {}), None
        else:
            return {}, f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError as e:
        return {}, f"Connection refused - NetworkPolicy may be blocking traffic"
    except requests.exceptions.Timeout:
        return {}, "Request timeout"
    except Exception as e:
        return {}, str(e)

@app.route('/')
def index():
    inventory, error = fetch_inventory()
    return render_template_string(
        ORDER_TEMPLATE,
        inventory=inventory,
        error=error,
        pod_name=os.getenv('HOSTNAME', 'unknown'),
        inventory_url=INVENTORY_URL
    )

@app.route('/order', methods=['POST'])
def place_order():
    """Place order by reserving item from inventory"""
    data = request.get_json()
    item = data.get('item')
    quantity = data.get('quantity', 1)

    try:
        response = requests.post(
            f'{INVENTORY_URL}/reserve',
            json={'item': item, 'quantity': quantity},
            timeout=3
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("🛍️ Starting Order Service...")
    print(f"Pod: {os.getenv('HOSTNAME', 'unknown')}")
    print(f"Inventory Service: {INVENTORY_URL}")
    app.run(host='0.0.0.0', port=5000)
