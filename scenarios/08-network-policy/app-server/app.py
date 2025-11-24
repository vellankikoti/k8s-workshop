#!/usr/bin/env python3
"""
Inventory Service - Backend service for product inventory
Demonstrates NetworkPolicy - receives requests from order service
"""
from flask import Flask, jsonify, request
import os
from datetime import datetime

app = Flask(__name__)

# Sample inventory data
INVENTORY = {
    'laptop': {'name': 'Laptop', 'stock': 50, 'price': 999.99},
    'mouse': {'name': 'Wireless Mouse', 'stock': 200, 'price': 29.99},
    'keyboard': {'name': 'Mechanical Keyboard', 'stock': 75, 'price': 149.99},
    'monitor': {'name': '4K Monitor', 'stock': 30, 'price': 399.99},
    'headphones': {'name': 'Noise-Canceling Headphones', 'stock': 100, 'price': 299.99}
}

@app.route('/')
def index():
    return jsonify({
        'service': 'Inventory Service',
        'status': 'running',
        'pod': os.getenv('HOSTNAME', 'unknown'),
        'endpoints': ['/inventory', '/check/<item>', '/reserve']
    })

@app.route('/inventory')
def get_inventory():
    """Get full inventory list"""
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'inventory': INVENTORY,
        'total_items': len(INVENTORY)
    })

@app.route('/check/<item>')
def check_stock(item):
    """Check stock for specific item"""
    item = item.lower()
    if item in INVENTORY:
        return jsonify({
            'item': item,
            'available': True,
            'stock': INVENTORY[item]['stock'],
            'price': INVENTORY[item]['price']
        })
    else:
        return jsonify({
            'item': item,
            'available': False,
            'message': 'Item not found'
        }), 404

@app.route('/reserve', methods=['POST'])
def reserve_item():
    """Reserve item from inventory"""
    data = request.get_json()
    item = data.get('item', '').lower()
    quantity = data.get('quantity', 1)

    if item not in INVENTORY:
        return jsonify({'error': 'Item not found'}), 404

    if INVENTORY[item]['stock'] >= quantity:
        INVENTORY[item]['stock'] -= quantity
        return jsonify({
            'success': True,
            'item': item,
            'reserved': quantity,
            'remaining_stock': INVENTORY[item]['stock']
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Insufficient stock',
            'available': INVENTORY[item]['stock']
        }), 400

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("🏪 Starting Inventory Service...")
    print(f"Pod: {os.getenv('HOSTNAME', 'unknown')}")
    print(f"Inventory items: {len(INVENTORY)}")
    app.run(host='0.0.0.0', port=5000)
