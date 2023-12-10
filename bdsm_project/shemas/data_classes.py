from typing import Optional

from pydantic import BaseModel


class MetaData(BaseModel):
    time: Optional[int] = None
    user_id: Optional[int] = None
    chat_id: Optional[int] = None


class Message(BaseModel):
    text: str = ""
    api_type: str = "not-stated"
    meta: MetaData
    image_path: Optional[str] = None
    raw_image: Optional[str] = None


class VKMessage(Message):
    # Example of attachment string
    # {type}{owner_id}_{media_id}_{access_key}
    attachment: Optional[str] = None
