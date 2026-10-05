import gradio as gr

from openAIchat.chat import client, openAI_config, summary  # one shared Summary
from schemas import Message, Content, ContextType, ImageUrl, Roles
from utils import image_reader, read_system_prompt

SYSTEM_PROMPT_PATH = "/workplace/openAIchat/system_prompt.txt"
MAX_REPLY_TOKENS = 4096  # thinking tokens count too
HISTORY_BUDGET = 24_000  # keep below the model's trained context length
KEEP_IMAGES = 2  # only the newest N images stay in history
IMAGE_TOKENS = 1500  # rough cost of one image

history: list[Message] = []  # single-user, in-memory


def text_of(msg: Message) -> str:
    if isinstance(msg.content, str):
        return msg.content
    return " ".join(c.text for c in msg.content if c.text)


def n_images(msg: Message) -> int:
    if isinstance(msg.content, str):
        return 0
    return sum(1 for c in msg.content if c.image_url)


def est(msg: Message) -> int:
    return len(text_of(msg)) // 3 + 4 + n_images(msg) * IMAGE_TOKENS


def total() -> int:
    return sum(est(m) for m in history) + len(summary.summary) // 3


def drop_old_images() -> None:
    seen = 0
    for msg in reversed(history):
        if n_images(msg):
            seen += 1
            if seen > KEEP_IMAGES:
                msg.content = text_of(msg)


def trim() -> None:
    """Summarize and remove the oldest messages, down to ~60% of the budget."""
    target = HISTORY_BUDGET * 0.6
    cut = 0
    while cut < len(history) - 2 and sum(est(m) for m in history[cut:]) > target:
        cut += 1
    while cut < len(history) - 1 and history[cut].role is not Roles.USER:
        cut += 1
    if cut <= 0:
        return
    chunk: list[Message] = []
    if summary.summary.strip():  # carry the previous summary forward
        chunk.append(Message(role=Roles.ASSISTANT, content=summary.summary))
    # text only, so base64 images never end up in the summary prompt
    chunk += [Message(role=m.role, content=text_of(m)) for m in history[:cut]]
    summary.make_summary(chunk)
    del history[:cut]


def system_text() -> str:
    text = read_system_prompt(SYSTEM_PROMPT_PATH).content
    if summary.summary.strip():
        text += "\n\n" + summary.summary
    return text


def chat(message, gradio_history):
    if not gradio_history:  # new chat (first message or after Clear)
        history.clear()
        summary.summary = ""

    text = message.get("text", "") if isinstance(message, dict) else str(message)
    files = message.get("files", []) if isinstance(message, dict) else []
    if not text.strip() and not files:
        return

    if files:
        parts = [Content(text=text or " ")]
        for f in files:
            path = f if isinstance(f, str) else f.get("path")
            parts.append(
                Content(
                    type=ContextType.IMAGE_URL.value,
                    image_url=ImageUrl(url=image_reader(path)),
                )
            )
        history.append(Message(role=Roles.USER, content=parts))
    else:
        history.append(Message(role=Roles.USER, content=text))
    drop_old_images()

    cfg = openAI_config.model_dump()
    cfg["max_tokens"] = MAX_REPLY_TOKENS
    messages = [{"role": "system", "content": system_text()}] + [
        m.model_dump(mode="json", exclude_none=True) for m in history
    ]

    reply, finish = "", None
    try:
        stream = client.chat.completions.create(messages=messages, stream=True, **cfg)
        for chunk in stream:
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            if choice.delta.content:
                reply += choice.delta.content
                yield reply
            if choice.finish_reason:
                finish = choice.finish_reason
    except Exception as e:  # server down, bad request, ...
        history.pop()
        yield f"Request failed: {e}"
        return

    if finish == "length":
        if not reply:
            reply = "(No answer: the token limit was used up before the reply started.)"
        yield reply + '\n\n*Cut off by the reply token limit. Send "continue" to resume.*'
    history.append(Message(role=Roles.ASSISTANT, content=reply))

    if total() > HISTORY_BUDGET:
        yield reply + "\n\n*Summarizing older messages…*"
        try:
            trim()
        except Exception as e:
            yield reply + f"\n\n*Could not summarize older messages: {e}*"
            return
        yield reply


demo = gr.ChatInterface(
    chat,
    multimodal=True,
    textbox=gr.MultimodalTextbox(
        file_types=["image"], placeholder="Message, or attach an image"
    ),
    title="Local chat",
    fill_height=True,
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
