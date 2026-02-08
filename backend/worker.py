import time
import requests
import redis
import json
import os
from datetime import datetime

API_URL = os.getenv("API_URL", "http://localhost:5000")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
WORKER_ID = os.getenv("WORKER_ID", "worker-1")

redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def execute_task(task):
    """Simulate doing the actual work"""
    task_type = task['type']
    task_data = task['data']
    
    print(f"[{WORKER_ID}] [{datetime.now().strftime('%H:%M:%S')}] Executing task {task['id']}: {task_type}")
    
    if task_type == "send_email":
        print(f"[{WORKER_ID}]   → Sending email to {task_data.get('to')}")
        time.sleep(2)
        print(f"[{WORKER_ID}]   ✓ Email sent!")
        
    elif task_type == "process_video":
        print(f"[{WORKER_ID}]   → Processing video {task_data.get('file')}")
        time.sleep(3)
        print(f"[{WORKER_ID}]   ✓ Video processed!")
        
    else:
        print(f"[{WORKER_ID}]   ⚠ Unknown task type: {task_type}")

def worker_loop():
    print(f"[{WORKER_ID}] Worker started! Waiting for tasks from Redis queue...")
    
    while True:
        try:
            result = redis_client.brpop('task_queue', timeout=2)
            
            if result:
                _, task_id = result
                task_id = int(task_id)
                
                response = requests.get(f"{API_URL}/tasks/{task_id}")
                task = response.json()
                
                if task['status'] == 'pending':
                    requests.patch(f"{API_URL}/tasks/{task_id}", 
                                 json={'status': 'running'})
                    
                    execute_task(task)
                    
                    requests.patch(f"{API_URL}/tasks/{task_id}", 
                                 json={'status': 'completed'})
                    print(f"[{WORKER_ID}]   ✓ Task {task_id} completed!\n")
                
        except Exception as e:
            print(f"[{WORKER_ID}] Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    worker_loop()