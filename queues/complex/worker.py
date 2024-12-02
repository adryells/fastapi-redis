from redis import Redis
from rq import Worker, Queue

redis_connection = Redis(port=6379, db=0)

queue = Queue(connection=redis_connection)

if __name__ == "__main__":
    worker = Worker([queue], connection=redis_connection)
    worker.work()
