import httpx
import base64

from utils import image_reader
from schemas import ContextType, ImageUrl, Content


def image_contents(paths: list[str]) -> list[Content]:
    return [
        Content(
            type=ContextType.IMAGE_URL.value,
            image_url=ImageUrl(url=image_reader(path)),
        )
        for path in paths
    ]


def image_content_from_internet(urls: list[str]):
    return [
        Content(
            type=ContextType.IMAGE_URL.value,
            image_url=ImageUrl(url=image_from_internet(url)),
        )
        for url in urls
    ]


def image_from_internet(url: str) -> str:
    response = httpx.get(url, timeout=15, follow_redirects=True)
    response.raise_for_status()
    mime_type = response.headers.get("content-type", "").split(";")[0]
    if not mime_type.startswith("image/"):
        raise ValueError(f"Not a direct image link: {url}")
    encoded = base64.b64encode(response.content).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"
