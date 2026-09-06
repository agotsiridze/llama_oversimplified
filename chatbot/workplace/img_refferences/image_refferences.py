from utils import image_refferences
from schemas import ContextType, ImageUrl, Content


def get_image_contents() -> list[Content]:
    image_contents = [
        Content(type=ContextType.IMAGE_URL.value, image_url=ImageUrl(url=image))
        for image in image_refferences()
    ]
    return image_contents
