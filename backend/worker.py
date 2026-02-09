import time
import requests
import redis
import json
import os
import random
import threading
from datetime import datetime

API_URL = os.getenv("API_URL", "http://localhost:5000")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
WORKER_ID = os.getenv("WORKER_ID", "worker-1")

redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

PRIORITY_QUEUES = ['task_queue_high', 'task_queue_medium', 'task_queue_low']

def send_heartbeat():
    """Send heartbeat to API every 10 seconds"""
    while True:
        try:
            requests.post(f"{API_URL}/workers/heartbeat", 
                        json={'worker_id': WORKER_ID})
        except Exception as e:
            print(f"[{WORKER_ID}] Heartbeat failed: {e}")
        time.sleep(10)

def execute_task(task):
    """Simulate doing the actual work - with random failures for testing retry"""
    task_type = task['type']
    task_data = task['data']
    task_id = task['id']
    retry_count = task.get('retry_count', 0)
    priority = task.get('priority', 'medium')
    
    print(f"[{WORKER_ID}] [{datetime.now().strftime('%H:%M:%S')}] Executing task {task_id}: {task_type} [Priority: {priority.upper()}] (Attempt {retry_count + 1})")
    
    if random.random() < 0.1 and retry_count < 2:
        print(f"[{WORKER_ID}]   ✗ Task failed! Will retry...")
        raise Exception(f"Simulated failure for task {task_id}")
    
    if task_type == "send_email":
        print(f"[{WORKER_ID}]   → Sending email to {task_data.get('to')}")
        time.sleep(2)
        print(f"[{WORKER_ID}]   ✓ Email sent!")
        
    elif task_type == "process_video":
        print(f"[{WORKER_ID}]   → Processing video {task_data.get('file')}")
        time.sleep(3)
        print(f"[{WORKER_ID}]   ✓ Video processed!")
        
    elif task_type == "generate_report":
        print(f"[{WORKER_ID}]   → Generating report: {task_data.get('report_type')}")
        time.sleep(4)
        print(f"[{WORKER_ID}]   ✓ Report generated!")
        
    elif task_type == "data_backup":
        print(f"[{WORKER_ID}]   → Backing up {task_data.get('database')}")
        time.sleep(5)
        print(f"[{WORKER_ID}]   ✓ Backup completed!")
        
    elif task_type == "image_processing":
        print(f"[{WORKER_ID}]   → Processing image: {task_data.get('image_path')}")
        time.sleep(3)
        print(f"[{WORKER_ID}]   ✓ Image processed!")
        
    elif task_type == "send_notification":
        print(f"[{WORKER_ID}]   → Sending notification to {task_data.get('user_id')}")
        time.sleep(1)
        print(f"[{WORKER_ID}]   ✓ Notification sent!")
        
    elif task_type == "run_ml_model":
        print(f"[{WORKER_ID}]   → Running ML model: {task_data.get('model_name')}")
        time.sleep(6)
        print(f"[{WORKER_ID}]   ✓ Model executed!")
        
    elif task_type == "webhook_trigger":
        print(f"[{WORKER_ID}]   → Triggering webhook: {task_data.get('url')}")
        time.sleep(2)
        print(f"[{WORKER_ID}]   ✓ Webhook triggered!")
        
    else:
        print(f"[{WORKER_ID}]   ⚠ Unknown task type: {task_type}")

def get_next_task():
    """Get next task from highest priority queue that has tasks"""
    for queue in PRIORITY_QUEUES:
        result = redis_client.brpop(queue, timeout=1)
        if result:
            return result
    return None

def worker_loop():
    print(f"[{WORKER_ID}] Worker started! Waiting for tasks from priority queues...")
    print(f"[{WORKER_ID}] Queue priority: HIGH > MEDIUM > LOW")
    print(f"[{WORKER_ID}] Heartbeat enabled - sending every 10s")
    
    
    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()
    
    while True:
        try:
            result = get_next_task()
            
            if result:
                _, task_id = result
                task_id = int(task_id)
                
                response = requests.get(f"{API_URL}/tasks/{task_id}")
                task = response.json()
                
                if task['status'] == 'pending':
                    requests.patch(f"{API_URL}/tasks/{task_id}", 
                                 json={'status': 'running'})
                    
                    try:
                        retry_count = task.get('retry_count', 0)
                        if retry_count > 0:
                            delay = min(2 ** retry_count, 30)
                            print(f"[{WORKER_ID}] Waiting {delay}s before retry...")
                            time.sleep(delay)
                        
                        execute_task(task)
                        
                        requests.patch(f"{API_URL}/tasks/{task_id}", 
                                     json={'status': 'completed'})
                        print(f"[{WORKER_ID}]   ✓ Task {task_id} completed!\n")
                        
                    except Exception as e:
                        print(f"[{WORKER_ID}]   ✗ Task {task_id} failed: {str(e)}")
                        requests.patch(f"{API_URL}/tasks/{task_id}", 
                                     json={
                                         'status': 'failed',
                                         'error_message': str(e)
                                     })
                        print()
            else:
                time.sleep(1)
                
        except Exception as e:
            print(f"[{WORKER_ID}] Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    worker_loop()