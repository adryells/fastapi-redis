import json
import requests
import redis
import time
import sqlite3

import uvicorn
from fastapi import FastAPI

rd = redis.Redis(port=6379, db=0)

conn = sqlite3.connect("test.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS anime_data (
    id INTEGER PRIMARY KEY,
    data TEXT
)
""")
conn.commit()

app = FastAPI()

@app.get("/")
def get_anime_list():
    start_time = time.time()

    cache_key = "marianaaa"

    cache = rd.get(cache_key)
    if cache:
        print("FROM CACHE")
        data = json.loads(cache)
    else:
        print("FETCHING FROM API")

        query = """
            query ($search: String) {
              Animes {
                animes(search: $search) {
                  totalCount
                  items {
                    id
                    synopsis
                    numEpisodes
                    name
                    averageEpDuration
                    totalHours
                    totalDays
                    active
                    relatedMedia {
                      url
                      sizeTypeId
                    }
                  }
                }
              }
            }
        """
        request_query = {
            'variables': {},
            'query': query
        }
        response = requests.post(
            "https://tfa-api.vercel.app/graphql",
            json=request_query,
            headers={'content_type': 'application/json'}
        )
        data = response.json()

        rd.setex(cache_key, 60, json.dumps(data))

        cursor.execute("INSERT INTO anime_data (data) VALUES (?)", (json.dumps(data),))
        conn.commit()

    elapsed_time = time.time() - start_time
    print(f"Tempo de execução: {elapsed_time:.4f} segundos")
    return data

uvicorn.run(app)