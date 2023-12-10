from abc import ABC, abstractmethod
from enum import Enum
from queue import Queue
from typing import Optional

from pydantic import BaseModel


class APIType(Enum):
    VkGroupChat = 1
    VkUserChat = 2
    TGUserChat = 3


class MetaData(BaseModel):
    time: Optional[int] = None
    user_id: Optional[int] = None
    chat_id: Optional[int] = None


class Message(BaseModel):
    text: str = ""
    meta: MetaData


class VKMessage(Message):
    # Example of attachment string
    # {type}{owner_id}_{media_id}_{access_key}
    attachment: Optional[str] = None
    photo_path: Optional[str] = None
    raw_photo: Optional[str] = None


class Task(BaseModel):
    text: str
    api_type: APIType
    meta: MetaData


class BaseApiManager(ABC):
    server_name = "BaseName"
    answers_q: Queue[Message] = Queue()

    def get_server_name(self) -> str:
        return self.server_name

    @abstractmethod
    async def main_loop(self) -> None:
        "Recieving messages from API. Main loop of program"
        raise NotImplementedError("main_loop method is not implemeted")

    @abstractmethod
    async def send_message_to_user(self, message: Message) -> None:
        "Sending message from api manager to client"
        raise NotImplementedError("send_message_to_user method is not implemeted")

    @abstractmethod
    async def add_task(self, task: Task) -> None:
        "Add task to TaskManager"
        raise NotImplementedError("add_task method is not implemeted")

    @abstractmethod
    async def add_answer(self, message: Message) -> None:
        "Add answer from TaskManager into answers queue"
        raise NotImplementedError("add_answer method is not implemeted")
