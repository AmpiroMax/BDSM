from typing import Optional

import requests
from PIL import Image

from bdsm_project.utils.serialization import obj2str


def send_message(text: str, chat_id: int) -> None:
    "Send task to TaskManager"

    data = {
        "text": text,
        "meta": {"chat_id": chat_id}
    }
    url = "http://localhost:8083/add_answer"
    output = requests.post(url, json=data).json()
    print(output)


def send_image(image_path: str, chat_id: int) -> None:
    image = Image.open(image_path)
    raw_image = obj2str(image)
    data = {
        "raw_photo": raw_image,
        "meta": {"chat_id": chat_id}
    }

    url = "http://localhost:8083/add_answer"
    output = requests.post(url, json=data).json()
    print(output)


def send_message_with_image(
    chat_id: int,
    text: Optional[str] = None,
    image_path: Optional[str] = None
) -> None:

    data = {"meta": {"chat_id": chat_id}}

    if text is not None:
        data["text"] = text

    if image_path is not None:
        image = Image.open(image_path)
        raw_image = obj2str(image)
        data["raw_photo"] = raw_image

    url = "http://localhost:8083/add_answer"
    output = requests.post(url, json=data).json()
    print(output)


if __name__ == "__main__":

    chat_id = 1
    text = """Hello мой друг!)"""
    image_path = "data/bridge.jpg"

    # send_message(text, chat_id)
    # send_image(image_path, chat_id)
    send_message_with_image(chat_id=chat_id, image_path=image_path)
