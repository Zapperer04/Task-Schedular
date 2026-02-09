from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import redis
from models import SessionLocal, Task

app = Flask(__name__)
CORS(app)

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


PRIORITY_QUEUES = {
    'high': 'task_queue_high',
    'medium': 'task_queue_medium',
    'low': 'task_queue_low'
}


WORKER_HEARTBEAT_EXPIRY = 30

def check_dependencies_met(task_id, db):
    """Check if all dependencies for a task are completed"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or not task.dependencies:
        return True
    
    dependency_ids = json.loads(task.dependencies)
    if not dependency_ids:
        return True
    
    for dep_id in dependency_ids:
        dep_task = db.query(Task).filter(Task.id == dep_id).first()
        if not dep_task or dep_task.status != 'completed':
            return False
    
    return True

def add_task_to_queue(task_id, priority='medium'):
    """Add task to appropriate priority queue"""
    queue_name = PRIORITY_QUEUES.get(priority, 'task_queue_medium')
    redis_client.lpush(queue_name, task_id)

@app.route('/tasks', methods=['POST'])
def create_task():
    db = SessionLocal()
    try:
        data = request.json
        
        dependencies = data.get('dependencies', [])
        if dependencies:
            for dep_id in dependencies:
                dep_task = db.query(Task).filter(Task.id == dep_id).first()
                if not dep_task:
                    return jsonify({'error': f'Dependency task {dep_id} not found'}), 400
        
        priority = data.get('priority', 'medium')
        if priority not in ['high', 'medium', 'low']:
            return jsonify({'error': 'Priority must be high, medium, or low'}), 400
        
        task = Task(
            type=data.get('type'),
            data=json.dumps(data.get('data', {})),
            priority=priority,
            dependencies=json.dumps(dependencies) if dependencies else None,
            max_retries=data.get('max_retries', 3),
            status='pending'
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        if check_dependencies_met(task.id, db):
            add_task_to_queue(task.id, priority)
        
        return jsonify(task.to_dict()), 201
    finally:
        db.close()

@app.route('/tasks', methods=['GET'])
def get_tasks():
    db = SessionLocal()
    try:
        tasks = db.query(Task).order_by(Task.id.desc()).all()
        return jsonify([task.to_dict() for task in tasks])
    finally:
        db.close()

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(task.to_dict())
    finally:
        db.close()

@app.route('/tasks/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.json
        
        if 'status' in data:
            task.status = data['status']
            
            if data['status'] == 'running':
                task.started_at = datetime.now()
                
            elif data['status'] == 'completed':
                task.completed_at = datetime.now()
                
                waiting_tasks = db.query(Task).filter(Task.status == 'pending').all()
                for waiting_task in waiting_tasks:
                    if waiting_task.dependencies and check_dependencies_met(waiting_task.id, db):
                        add_task_to_queue(waiting_task.id, waiting_task.priority)
            
            elif data['status'] == 'failed':
                task.retry_count += 1
                task.error_message = data.get('error_message', 'Unknown error')
                
                if task.retry_count < task.max_retries:
                    print(f"Task {task_id} failed. Retry {task.retry_count}/{task.max_retries}")
                    task.status = 'pending'
                    add_task_to_queue(task_id, task.priority)
                else:
                    print(f"Task {task_id} failed permanently after {task.retry_count} retries")
        
        db.commit()
        db.refresh(task)
        return jsonify(task.to_dict())
    finally:
        db.close()


@app.route('/workers/heartbeat', methods=['POST'])
def worker_heartbeat():
    data = request.json
    worker_id = data.get('worker_id')
    
    if not worker_id:
        return jsonify({'error': 'worker_id required'}), 400
    
    
    worker_key = f'worker:{worker_id}'
    worker_data = {
        'worker_id': worker_id,
        'last_seen': datetime.now().isoformat(),
        'status': 'active'
    }
    
    redis_client.setex(
        worker_key,
        WORKER_HEARTBEAT_EXPIRY,
        json.dumps(worker_data)
    )
    
    return jsonify({'status': 'ok'}), 200


@app.route('/workers', methods=['GET'])
def get_workers():
    worker_keys = redis_client.keys('worker:*')
    workers = []
    
    for key in worker_keys:
        worker_data = redis_client.get(key)
        if worker_data:
            workers.append(json.loads(worker_data))
    
    return jsonify(workers), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)