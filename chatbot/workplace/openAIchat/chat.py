from typing import Any

from openai import OpenAI

from config import OpenAIConfig
from schemas import Message, Content, Roles, ChatReply
from img_refferences import image_contents, image_content_from_internet
from utils import Summary

client = OpenAI(base_url="http://llama_cpp_server:8081/v1", api_key="none")
openAI_config = OpenAIConfig()
summary = Summary()


SUMMARY_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_context",
        "description": "Retrieves long-term summary context containing archived chat history and past user facts.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}


def handle_tool_calls(
    response, history_dict: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    assistant_msg = response.choices[0].message
    for call in assistant_msg.tool_calls:
        if call.function.name == "read_context":
            # Grabs the dynamic text directly from your instance property
            context_data = summary.read_context()

            history_dict.append(assistant_msg)
            history_dict.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": call.function.name,
                    "content": str(context_data),
                }
            )
    return history_dict


def message_in_chat(
    system_prompts: Message, history: list[Message], thinking: bool = False
) -> ChatReply:
    history_dict = [msg.model_dump(mode="json", exclude_none=True) for msg in history]
    system_prompt_dict = system_prompts.model_dump(mode="json", exclude_none=True)

    response = client.chat.completions.create(
        messages=[system_prompt_dict] + history_dict,
        **openAI_config.model_dump(),
        extra_body={"chat_template_kwargs": {"enable_thinking": thinking}},
    )
    choice = response.choices[0]
    reply = ChatReply(
        text=choice.message.content or "",
        thinking=getattr(choice.message, "reasoning_content", None) or "",
        finish_reason=choice.finish_reason,
    )
    return reply


def message_factory(
    input_text: str,
    role: Roles = Roles.USER,
    img_paths: list[str] = [],
    img_urls: list[str] = [],
) -> Message:
    if img_paths or img_urls:
        text_content = Content(text=input_text)
        images = image_contents(img_paths)
        from_internet = image_content_from_internet(img_urls)
        data_to_send = [text_content] + images + from_internet
        message = Message(role=role, content=data_to_send)
        return message
    return Message(role=role, content=input_text)
