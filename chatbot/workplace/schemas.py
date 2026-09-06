from pydantic import BaseModel
from enum import Enum


class Roles(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ContextType(str, Enum):
    TEXT = "text"
    IMAGE_URL = "image_url"


class ImageUrl(BaseModel):
    url: str


class Content(BaseModel):
    type: str = ContextType.TEXT.value
    text: str | None = None
    image_url: ImageUrl | None = None


class Message(BaseModel):
    role: Roles = Roles.USER
    content: list[Content] | str = []
