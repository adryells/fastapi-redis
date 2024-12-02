import redis
import time

redis_connection = redis.Redis(port=6379, db=0)
queue_name = "task_queue"

while True:
    task = redis_connection.blpop(queue_name, timeout=5)
    if task:
        queue_name, task_name = task
        print(f"Processing {task_name.decode('utf-8')}...")
        time.sleep(2)
    else:
        print("No tasks in the queue. Waiting...")

