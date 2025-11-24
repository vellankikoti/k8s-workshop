#!/usr/bin/env python3
"""
TODO App - Demonstrates init container usage
Init container sets up Redis database, main container runs TODO app
"""
from flask import Flask, render_template_string, request, jsonify
import redis
import os
import json
from datetime import datetime

app = Flask(__name__)

# Redis connection
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))

def connect_redis():
    """Connect to Redis"""
    try:
        r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        r.ping()
        print(f"✅ Connected to Redis at {redis_host}:{redis_port}")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"❌ Cannot connect to Redis: {e}")
        return None

r = connect_redis()

TODO_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>TODO App</title>
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
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .add-todo {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .todo-input {
            width: 70%;
            padding: 15px;
            border: 2px solid #667eea;
            border-radius: 5px;
            font-size: 1em;
        }
        .add-btn {
            width: 25%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            margin-left: 10px;
        }
        .add-btn:hover {
            opacity: 0.9;
        }
        .todo-list {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .todo-item {
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .todo-item.completed {
            opacity: 0.6;
            text-decoration: line-through;
        }
        .delete-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
        }
        .complete-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 5px;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #f5c6cb;
        }
        .init-status {
            background: #d1ecf1;
            color: #0c5460;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>✅ TODO App</h1>
        <p>Manage your tasks with Redis backend</p>
        <p style="font-size: 0.9em; opacity: 0.8;">Pod: {{ pod_name }}</p>
    </div>

    {% if db_ready %}
    <div class="init-status">
        <strong>✅ Database Ready:</strong> Init container successfully set up Redis connection
    </div>

    <div class="add-todo">
        <h2>Add New Task</h2>
        <form id="addForm">
            <input type="text" id="todoInput" class="todo-input" placeholder="What needs to be done?" required>
            <button type="submit" class="add-btn">Add Task</button>
        </form>
    </div>

    <div class="todo-list">
        <h2>Tasks ({{ todo_count }})</h2>
        {% if todos %}
        {% for todo in todos %}
        <div class="todo-item {% if todo.completed %}completed{% endif %}">
            <div>
                <strong>{{ todo.text }}</strong><br>
                <small>Created: {{ todo.created_at }}</small>
            </div>
            <div>
                {% if not todo.completed %}
                <button class="complete-btn" onclick="completeTodo('{{ todo.id }}')">✓ Complete</button>
                {% endif %}
                <button class="delete-btn" onclick="deleteTodo('{{ todo.id }}')">🗑️ Delete</button>
            </div>
        </div>
        {% endfor %}
        {% else %}
        <p style="text-align:center; color:#666">No tasks yet. Add one above!</p>
        {% endif %}
    </div>
    {% else %}
    <div class="error">
        <h2>❌ Database Not Ready</h2>
        <p>The init container failed to set up the Redis connection.</p>
        <p>Check init container logs for details.</p>
    </div>
    {% endif %}

    <script>
        document.getElementById('addForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const text = document.getElementById('todoInput').value;

            fetch('/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
        });

        function completeTodo(id) {
            fetch('/complete/' + id, {method: 'POST'})
            .then(() => location.reload());
        }

        function deleteTodo(id) {
            fetch('/delete/' + id, {method: 'POST'})
            .then(() => location.reload());
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    db_ready = r is not None
    todos = []
    todo_count = 0

    if db_ready:
        # Get all todo IDs
        todo_ids = r.lrange('todos', 0, -1)
        for todo_id in todo_ids:
            todo_data = r.get(f'todo:{todo_id}')
            if todo_data:
                todo = json.loads(todo_data)
                todos.append(todo)
        todo_count = len(todos)

    return render_template_string(
        TODO_TEMPLATE,
        db_ready=db_ready,
        todos=todos,
        todo_count=todo_count,
        pod_name=os.getenv('HOSTNAME', 'unknown')
    )

@app.route('/add', methods=['POST'])
def add_todo():
    """Add new todo"""
    if not r:
        return jsonify({'success': False, 'error': 'Database not ready'}), 503

    data = request.get_json()
    text = data.get('text', '')

    # Generate ID
    todo_id = r.incr('todo_counter')

    # Create todo
    todo = {
        'id': str(todo_id),
        'text': text,
        'completed': False,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Save to Redis
    r.set(f'todo:{todo_id}', json.dumps(todo))
    r.rpush('todos', todo_id)

    return jsonify({'success': True, 'id': todo_id})

@app.route('/complete/<todo_id>', methods=['POST'])
def complete_todo(todo_id):
    """Mark todo as completed"""
    if not r:
        return jsonify({'success': False}), 503

    todo_data = r.get(f'todo:{todo_id}')
    if todo_data:
        todo = json.loads(todo_data)
        todo['completed'] = True
        r.set(f'todo:{todo_id}', json.dumps(todo))

    return jsonify({'success': True})

@app.route('/delete/<todo_id>', methods=['POST'])
def delete_todo(todo_id):
    """Delete todo"""
    if not r:
        return jsonify({'success': False}), 503

    r.delete(f'todo:{todo_id}')
    r.lrem('todos', 0, todo_id)

    return jsonify({'success': True})

@app.route('/health')
def health():
    if r:
        try:
            r.ping()
            return jsonify({'status': 'healthy', 'database': 'connected'})
        except:
            return jsonify({'status': 'degraded', 'database': 'disconnected'}), 503
    return jsonify({'status': 'unhealthy', 'database': 'not ready'}), 503

if __name__ == '__main__':
    print("✅ Starting TODO App...")
    print(f"Redis: {redis_host}:{redis_port}")
    print(f"Database ready: {r is not None}")
    app.run(host='0.0.0.0', port=5000)
