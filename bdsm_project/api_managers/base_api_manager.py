from abc import ABC, abstractmethod
from queue import Queue

from bdsm_project.shemas.data_classes import Message


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
    async def add_task(self, task: Message) -> None:
        "Add task to TaskManager"
        raise NotImplementedError("add_task method is not implemeted")

    @abstractmethod
    async def add_answer(self, message: Message) -> None:
        "Add answer from TaskManager into answers queue"
        raise NotImplementedError("add_answer method is not implemeted")
