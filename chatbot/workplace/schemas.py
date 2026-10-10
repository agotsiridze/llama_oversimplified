from enum import Enum

from pydantic import BaseModel


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

    @property
    def text(self) -> str:
        """Text only, never base64 image data."""
        if isinstance(self.content, str):
            return self.content
        return " ".join(c.text for c in self.content if c.text)

    @property
    def image_count(self) -> int:
        if isinstance(self.content, str):
            return 0
        return sum(1 for c in self.content if c.image_url)


class ChatReply(BaseModel):
    """What the model returned, plus why it stopped."""

    text: str
    finish_reason: str | None = None
    thinking: str = ""

    @property
    def truncated(self) -> bool:
        return self.finish_reason == "length"

    def __str__(self) -> str:  # keeps print(reply) / str(reply) working
        return self.text
