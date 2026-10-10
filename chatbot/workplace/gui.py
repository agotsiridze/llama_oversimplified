import gradio as gr

from openAIchat.chat import message_factory, message_in_chat
from schemas import Message, Roles
from utils import read_system_prompt

SYSTEM_PROMPT_PATH = "/workplace/openAIchat/system_prompt.txt"

history: list[Message] = []
pending_links: list[str] = []


def add_link(link: str) -> tuple[str, str]:
    link = link.strip()
    if link:
        pending_links.append(link)
    return "", "\n".join(pending_links)


def respond(message: dict[str, str], gradio_history: list[str], thinking: bool):
    if not gradio_history:  # first message or after Clear
        history.clear()
    text = message["text"]
    paths = [f for f in message["files"]]
    if not text.strip() and not paths and not pending_links:
        return ""

    try:
        user_message = message_factory(text, img_paths=paths, img_urls=pending_links)
    except Exception as e:
        return f"Could not load the image: {e}"
    history.append(user_message)

    reply = message_in_chat(
        read_system_prompt(SYSTEM_PROMPT_PATH), history, thinking=thinking
    )

    history.append(message_factory(reply.text, Roles.ASSISTANT))
    pending_links.clear()
    if reply.thinking:
        return [
            gr.ChatMessage(content=reply.thinking, metadata={"title": "Thinking"}),
            gr.ChatMessage(content=reply.text),
        ]
    return reply.text


with gr.Blocks() as demo:
    with gr.Row():
        link_box = gr.Textbox(label="Image link", placeholder="https://...", scale=4)
        add_btn = gr.Button("Add", scale=1)
    added = gr.Textbox(label="Links for the next message", interactive=False)
    chat = gr.ChatInterface(
        respond,
        additional_inputs=[gr.Checkbox(label="Reasoning", value=False, render=False)],
        additional_inputs_accordion=gr.Accordion("Settings", open=True, render=False),
        multimodal=True,
        textbox=gr.MultimodalTextbox(
            file_types=["image"], placeholder="Message, or attach an image"
        ),
        title="Local chat",
    )
    add_btn.click(add_link, link_box, [link_box, added])
    chat.chatbot.change(lambda: "\n".join(pending_links), None, added)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
