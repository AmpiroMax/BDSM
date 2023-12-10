from abc import ABC, abstractmethod
from enum import Enum
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
    text: str
    meta: MetaData


class VKMessage(Message):
    # Example of attachment string
    # {type}{owner_id}_{media_id}_{access_key}
    attachment: Optional[str] = None


class Task(BaseModel):
    text: str
    api_type: APIType
    meta: MetaData


class BaseApiManager(ABC):
    server_name = "BaseName"

    def get_server_name(self) -> str:
        return self.server_name

    @abstractmethod
    async def main_loop(self) -> None:
        "Recieving messages from API. Main loop of program"
        raise NotImplementedError("main_loop method is not implemeted")

    @abstractmethod
    async def send_message(self, message: Message) -> None:
        "Sending message from api manager to client"
        raise NotImplementedError("send_message method is not implemeted")

    @abstractmethod
    async def put_task(self, task: Task) -> None:
        "Send task to TaskManager"
        raise NotImplementedError("put_task method is not implemeted")
