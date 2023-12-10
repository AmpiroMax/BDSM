import asyncio
import logging
from contextlib import asynccontextmanager
from queue import Queue

import requests
import uvicorn
import vk_api.vk_api
from base_api_manager import APIType, BaseApiManager, MetaData, Task, VKMessage
from fastapi import FastAPI
from pydantic import BaseModel
from secured_data import group_id, vk_api_token
from vk_api.bot_longpoll import VkBotEvent, VkBotEventType, VkBotLongPoll
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id

logging.basicConfig(
    level=logging.INFO,
    # filename="mylog.log",
    format="[%(asctime)s][%(module)s][%(levelname)s][%(funcName)s][line %(lineno)d] - %(message)s",
    datefmt='%H:%M:%S',
)
logger = logging.getLogger("VKAPI")


class VkGroupChatManager(BaseApiManager):

    def __init__(
        self,
        api_token: str,
        group_id: int,
        server_name: str = "VKGroupChatServer"
    ):
        logger.info("Initializing VkGroupChatManager")
        self.server_name = server_name

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

            await self.events_handler(events)
            await self.answers_handler()

            await asyncio.sleep(0.1)

    async def events_handler(self, events: list[VkBotEvent]) -> None:
        for event in events:
            if event.type == VkBotEventType.MESSAGE_NEW:
                message = event.object["message"]
                task = Task(
                    text=message["text"],
                    api_type=APIType.VkGroupChat,
                    meta=MetaData(
                        time=message["date"],
                        chat_id=event.chat_id
                    )
                )
                await self.put_task(task)

    async def answers_handler(self) -> None:
        while not self.answers_q.empty():
            answer = self.answers_q.get()
            await self.send_message(answer)

    async def send_message(self, message: VKMessage) -> None:
        logger.info("sending message")
        kwargs = {
            "random_id": get_random_id(),
            "chat_id": message.meta.chat_id,
            "message": message.text,
        }

        if message.attachment is not None:
            kwargs["attachment"] = message.attachment

        await self.vk_api.messages.send(
            **kwargs
        )

    async def put_task(self, task: Task) -> None:
        "Send task to TaskManager"

        logger.info("forwading task")
        url = "http://localhost:8082/add_task"

        output = requests.post(url, json=task)
        logger.info(output)

    async def _upload_photo(self, photo_path: str) -> str:
        logger.info("uploading photo")
        response = await self.vk_upload.photo_messages(photo_path)[0]

        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']

        attachment = f'photo{owner_id}_{photo_id}_{access_key}'
        return attachment


if __name__ == "__main__":

    vk_group_chat_manager = VkGroupChatManager(vk_api_token, group_id)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        asyncio.ensure_future(vk_group_chat_manager.main_loop())
        yield
        pass

    app = FastAPI(lifespan=lifespan)

    class Text(BaseModel):
        text: str

    @app.post("/send_message")
    async def send_message(message: VKMessage):
        await vk_group_chat_manager.send_message(message=message)

    uvicorn.run(app, host="localhost", port=8083)
