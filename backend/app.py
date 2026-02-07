from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)


tasks = {}
task_id_counter = 1

@app.route('/tasks', methods=['POST'])
def create_task():
    global task_id_counter
    
    data = request.json
    task = {
        'id': task_id_counter,
        'type': data.get('type'),
        'data': data.get('data'),
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    
    tasks[task_id_counter] = task
    task_id_counter += 1
    
    return jsonify(task), 201

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(list(tasks.values()))

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task)

@app.route('/tasks/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.json
    
    # Update status if provided
    if 'status' in data:
        task['status'] = data['status']
    
    # Update completed_at timestamp if task is completed
    if data.get('status') == 'completed':
        task['completed_at'] = datetime.now().isoformat()
    
    return jsonify(task)

if __name__ == '__main__':
    app.run(debug=True, port=5000)