from rq import Queue
from redis import Redis
from tasks import process_data
import uuid

redis_connection = Redis(port=6379, db=0)

queue = Queue(connection=redis_connection)


def create_task(data: dict):
    task_id = str(uuid.uuid4())

    job = queue.enqueue(process_data, data, job_id=task_id)

    return job.id


def get_task_status(task_id: str):
    job = queue.fetch_job(task_id)
    if job:
        return {
            "task_id": job.id,
            "status": job.get_status(),
            "result": job.return_value,
        }
    return {"error": "Task not found"}


def get_all_tasks():
    for job in queue.jobs:
        print({
            "task_id": job.id,
            "status": job.get_status(),
            "result": job.return_value,
            "enqueued_at": job.enqueued_at,
            "started_at": job.started_at,
            "ended_at": job.ended_at,
        })


if __name__ == "__main__":
    task_0 = create_task(data={
        "bundol": 1,
        "bundil": True,
        "bundel": "lalala"
    })

    task_1 = create_task(
        data={
            "i_only_want_peace": "wowwwww",
            "segunda_feira": 111
        }
    )

    task_2 = create_task(
        data={
            "sabe_mto": "narutin",
            "sabe_pco": "sasukin"
        }
    )

    for task_id in [task_0, task_1, task_2, "xerecudo_senpai"]:
        print(get_task_status(task_id))

    print(get_all_tasks())
