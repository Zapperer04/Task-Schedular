import time
import requests
import redis
import json
from datetime import datetime

API_URL = "http://localhost:5000"
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def execute_task(task):
    """Simulate doing the actual work"""
    task_type = task['type']
    task_data = task['data']
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Executing task {task['id']}: {task_type}")
    
    if task_type == "send_email":
        print(f"  → Sending email to {task_data.get('to')}")
        time.sleep(2)
        print(f"  ✓ Email sent!")
        
    elif task_type == "process_video":
        print(f"  → Processing video {task_data.get('file')}")
        time.sleep(3)
        print(f"  ✓ Video processed!")
        
    else:
        print(f"  ⚠ Unknown task type: {task_type}")

def worker_loop():
    print("Worker started! Waiting for tasks from Redis queue...")
    
    while True:
        try:
            # Block and wait for a task from Redis queue
            result = redis_client.brpop('task_queue', timeout=2)
            
            if result:
                _, task_id = result
                task_id = int(task_id)
                
                # Get task details from API
                response = requests.get(f"{API_URL}/tasks/{task_id}")
                task = response.json()
                
                if task['status'] == 'pending':
                    # Mark as running
                    requests.patch(f"{API_URL}/tasks/{task_id}", 
                                 json={'status': 'running'})
                    
                    # Execute it
                    execute_task(task)
                    
                    # Mark as completed
                    requests.patch(f"{API_URL}/tasks/{task_id}", 
                                 json={'status': 'completed'})
                    print(f"  ✓ Task {task_id} completed!\n")
            else:
                # Timeout, no tasks available
                pass
                
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    worker_loop()