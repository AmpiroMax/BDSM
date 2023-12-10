import redis
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


class Data(BaseModel):
    key: str
    value: str


class RedisDB:
    def __init__(self):
        self.db = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def set(self, data: Data) -> None:
        self.db.set(data.key, data.value)

    def get(self, key: str) -> str:
        value = self.db.get(key)
        return value


if __name__ == "__main__":
    data_base = RedisDB()

    app = FastAPI()

    @app.post("/add_to_db")
    async def add_to_db(data: Data):
        data_base.set(data=data)

    @app.get("/get_from_db/{key}")
    async def get_from_db(key: str):
        return data_base.get(key=key)

    uvicorn.run(app, host="localhost", port=8085)
