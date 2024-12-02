import redis

redis_connection = redis.Redis(port=6379, db=0)

tasks = ["task1", "task2", "task3"]

for task in tasks:
    redis_connection.lpush("task_queue", task)
    print(f"Task {task} added.")
