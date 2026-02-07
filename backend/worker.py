import time
import requests
from datetime import datetime

API_URL = "http://localhost:5000"

def execute_task(task):
    """Simulate doing the actual work"""
    task_type = task['type']
    task_data = task['data']
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Executing task {task['id']}: {task_type}")
    
    if task_type == "send_email":
        # Simulate sending email
        print(f"  → Sending email to {task_data.get('to')}")
        time.sleep(2)  # Simulate work taking 2 seconds
        print(f"  ✓ Email sent!")
        
    elif task_type == "process_video":
        # Simulate processing video
        print(f"  → Processing video {task_data.get('file')}")
        time.sleep(3)  # Simulate work taking 3 seconds
        print(f"  ✓ Video processed!")
        
    else:
        print(f"  ⚠ Unknown task type: {task_type}")

def worker_loop():
    print("Worker started! Waiting for tasks...")
    
    while True:
        try:
            # Get all pending tasks
            response = requests.get(f"{API_URL}/tasks")
            tasks = response.json()
            
            # Find pending tasks
            pending_tasks = [t for t in tasks if t['status'] == 'pending']
            
            if pending_tasks:
                # Pick the first pending task
                task = pending_tasks[0]
                task_id = task['id']
                
                # Mark as running
                requests.patch(f"{API_URL}/tasks/{task_id}", 
                             json={'status': 'running'})
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Task {task_id} started")
                
                # Execute it
                execute_task(task)
                
                # Mark as completed
                requests.patch(f"{API_URL}/tasks/{task_id}", 
                             json={'status': 'completed'})
                print(f"  ✓ Task {task_id} completed!\n")
            else:
                # No tasks, wait a bit
                print("No pending tasks, waiting...")
                time.sleep(2)
                
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    worker_loop()