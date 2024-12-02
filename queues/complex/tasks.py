import time

def process_data(data: dict) -> dict:
    print(f"Processing: {data}")
    time.sleep(5)

    result = {"status": "success", "processed_data": data}
    print(f"Finishing: {data}")

    return result
