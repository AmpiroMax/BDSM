import asyncio
import logging
from asyncio import Queue
from contextlib import asynccontextmanager

import requests
import uvicorn
import vk_api.vk_api
from fastapi import FastAPI
from vk_api.bot_longpoll import VkBotEvent, VkBotEventType, VkBotLongPoll
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id

from bdsm_project.api_managers.base_api_manager import BaseApiManager
from bdsm_project.api_managers.secured_data import group_id, vk_api_token
from bdsm_project.shemas.data_classes import MetaData, VKMessage
from bdsm_project.utils.serialization import str2obj

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     [%(asctime)s][%(module)s][%(funcName)s][line %(lineno)d] - %(message)s",
    datefmt='%H:%M:%S',
)
logger = logging.getLogger("VKAPI")


class VkGroupChatManager(BaseApiManager):

    def __init__(
        self,
        api_token: str,
        group_id: int,
        server_name: str = "VKGroupChatServer",
        task_manager_port: int = 8085,
    ):
        logger.info("Initializing VkGroupChatManager")
        self.server_name = server_name
        self.task_manager_url = f"http://localhost:{task_manager_port}"
        self.answers_q: Queue[VKMessage] = Queue()

        # Base VK API handler
        self.vk = vk_api.VkApi(token=api_token)
        # VK group chats handler
        self.vk_long_poll = VkBotLongPoll(self.vk, group_id, wait=1)
        # VK API necessary for images upload
        self.vk_api = self.vk.get_api()
        self.vk_upload = VkUpload(self.vk_api)

    async def main_loop(self) -> None:
        logger.info("Starting main event loop")
        await asyncio.sleep(1)

        while True:
            events = self.vk_long_poll.check()

            await self._events_handler(events)
            await self._answers_handler()

            await asyncio.sleep(0.1)

    async def send_message_to_user(self, message: VKMessage) -> None:
        logger.info("Sending message...")
        kwargs = {
            "random_id": get_random_id(),
            "chat_id": message.meta.chat_id,
            "message": message.text,
        }

        if message.attachment is not None:
            kwargs["attachment"] = message.attachment

        self.vk_api.messages.send(
            **kwargs
        )
        logger.info("sending message - done.")

    async def add_task(self, task: VKMessage) -> None:
        "Send task to TaskManager"
        logger.info("Adding task")

        url = "http://localhost:8087/add_task"
        data = {
            "text": task.text,
            "meta": {"chat_id": task.meta.chat_id}
        }

        output = requests.post(url, json=data)

        logger.info(output)
        logger.info("Adding task - done.")

    async def add_answer(self, message: VKMessage) -> None:
        logger.info("Adding answer...")
        if message.raw_image is not None:
            # Hopefully it is a PIL Image and can be saved easily
            # any other cases must be taken into considiration
            photo = str2obj(message.raw_image)
            tmp_photo_path = "./generated.png"
            photo.save(tmp_photo_path)
            attachment = await self._upload_photo(tmp_photo_path)
            message.attachment = attachment

        self.answers_q.put_nowait(message)
        logger.info("Adding answer - done.")

    async def _events_handler(self, events: list[VkBotEvent]) -> None:
        for event in events:
            if event.type == VkBotEventType.MESSAGE_NEW:
                message = event.object["message"]
                if message["text"].split(" ")[0] == "/t2i":
                    text = " ".join(message["text"].split(" ")[1:])
                    logger.info(text)
                    task = VKMessage(
                        text=text,
                        api_type="vk_group",
                        meta=MetaData(
                            time=message["date"],
                            chat_id=event.chat_id
                        )
                    )
                    logger.info(task)
                    await self.add_task(task)
                    await self._add_to_db(task)

    async def _answers_handler(self) -> None:
        while not self.answers_q.empty():
            answer = self.answers_q.get_nowait()
            await self.send_message_to_user(answer)

    async def _upload_photo(self, photo_path: str) -> str:
        logger.info("uploading photo...")
        response = self.vk_upload.photo_messages(photo_path)[0]
        logger.info("uploading photo - done.")
        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']

        attachment = f'photo{owner_id}_{photo_id}_{access_key}'
        return attachment

    async def _add_to_db(self, message: VKMessage) -> None:
        "Add note to DataBase"
        logger.info("Adding note ot db...")
        key = f"{message.api_type}_{message.meta.time}_{message.meta.chat_id}"
        value = message.text

        url = "http://localhost:8085/add_to_db"
        data = {
            "key": key,
            "value": value
        }

        output = requests.post(url, json=data)

        logger.info(output)
        logger.info("Adding note ot db - done.")


if __name__ == "__main__":

    vk_group_chat_manager = VkGroupChatManager(vk_api_token, group_id)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        asyncio.ensure_future(vk_group_chat_manager.main_loop())
        yield
        pass

    app = FastAPI(lifespan=lifespan)

    @app.post("/add_answer")
    async def add_answer(message: VKMessage):
        await vk_group_chat_manager.add_answer(message=message)

    uvicorn.run(app, host="localhost", port=8083)
