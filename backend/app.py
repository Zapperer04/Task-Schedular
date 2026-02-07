from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import redis
from models import SessionLocal, Task

app = Flask(__name__)
CORS(app)

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.route('/tasks', methods=['POST'])
def create_task():
    db = SessionLocal()
    try:
        data = request.json
        
        # Create task in database
        task = Task(
            type=data.get('type'),
            data=json.dumps(data.get('data', {})),
            status='pending'
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Add task ID to Redis queue
        redis_client.lpush('task_queue', task.id)
        
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
        
        db.commit()
        db.refresh(task)
        return jsonify(task.to_dict())
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)