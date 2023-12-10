import asyncio
import logging
from asyncio import Queue
from contextlib import asynccontextmanager

import requests
import uvicorn
from fastapi import FastAPI

from bdsm_project.models.kandinskiy.model import MyKandinsky
from bdsm_project.shemas.data_classes import Message
from bdsm_project.utils.serialization import obj2str

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     [%(asctime)s][%(module)s][%(funcName)s][line %(lineno)d] - %(message)s",
    datefmt='%H:%M:%S',
)
logger = logging.getLogger("KandinskyServer")


class KandinskyServer:

    def __init__(self):
        self.model = MyKandinsky()
        self._task_q: Queue[Message] = Queue()
        self._answer_q: Queue[Message] = Queue()

    async def main_loop(self) -> None:
        while True:

            if not self._task_q.empty():
                try:
                    task = self._task_q.get_nowait()
                except Exception:
                    continue
                else:
                    await self._handle_task(task)

            if not self._answer_q.empty():
                try:
                    answer = self._answer_q.get_nowait()
                except Exception:
                    continue
                else:
                    await self._handle_answer(answer)

            await asyncio.sleep(0.1)

    async def add_task(self, message: Message) -> None:
        logger.info("Adding task...")
        self._task_q.put_nowait(message)
        logger.info("Adding task - done.")

    async def _handle_task(self, task: Message) -> None:
        logger.info("Handling task...")
        logger.info(f"Task text: {task.text}")

        image = self.model.text2img(task.text)
        raw_image = obj2str(image)
        task.raw_image = raw_image
        self._answer_q.put_nowait(task)
        logger.info("Handling task - done.")

    async def _handle_answer(self, answer: Message) -> None:
        logger.info("Handling answer...")
        url = "http://localhost:8083/add_answer"
        data = {
            "raw_image": answer.raw_image,
            "api_type": answer.api_type,
            "meta": {"chat_id": answer.meta.chat_id}
        }
        try:
            output = requests.post(url, json=data, timeout=3).json()
            logger.info(output)
        except requests.exceptions.Timeout:
            self._answer_q.put_nowait(answer)
            logger.info("Handling answer - TIMEOUT ")
        else:
            logger.info("Handling answer - done.")


if __name__ == "__main__":
    server = KandinskyServer()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        asyncio.ensure_future(server.main_loop())
        yield
        pass

    app = FastAPI(lifespan=lifespan)

    @app.post("/add_task")
    async def add_task(message: Message):
        await server.add_task(message)

    uvicorn.run(app, host='localhost', port=8087)
