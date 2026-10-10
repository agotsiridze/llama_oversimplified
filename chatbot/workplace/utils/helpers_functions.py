from config import Config
from schemas import Roles, Message

import os
import base64

config = Config()


def chat_to_model(
    messages, tokenizer, model, enable_thinking=False, tools=None
) -> tuple[list[dict[str, str]], str]:

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=enable_thinking,
        tools=tools,
    )

    if isinstance(text, list):
        # It's already IDs, just wrap in a tensor
        import torch

        model_inputs = {"input_ids": torch.tensor([text]).to(model.device)}
    else:
        # It's a string, tokenize it normally
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    # model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(**model_inputs, **config)
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]) :].tolist()
    try:
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(
        output_ids[:index], skip_special_tokens=True
    ).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

    return content, thinking_content


def read_system_prompt(path: str) -> Message:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    prompt = Message(role=Roles.SYSTEM, content=text)
    return prompt


def image_reader(path: str) -> str:
    with open(path, "rb") as image_file:
        encoded_bytes = base64.b64encode(image_file.read()).decode("utf-8")
    mime_type = path.split(".")[-1]
    if mime_type == "jpg":
        mime_type = "jpeg"
    base64_url = f"data:image/{mime_type};base64,{encoded_bytes}"
    return base64_url


def image_refferences() -> list[str]:
    img_dir = os.path.normpath("/workplace/img_refferences")
    paths = [
        os.path.join(img_dir, img)
        for img in os.listdir(img_dir)
        if img.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]
    images = [image_reader(image_url) for image_url in paths]
    return images
