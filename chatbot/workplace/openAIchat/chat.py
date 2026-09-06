from typing import Any

from openai import OpenAI

from config import OpenAIConfig
from schemas import Message, Content, Roles
from img_refferences import get_image_contents
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
    system_prompts: Message, history: list[Message], has_tools: bool = True
) -> str:
    history_dict = [msg.model_dump(mode="json", exclude_none=True) for msg in history]
    system_prompt_dict = system_prompts.model_dump(mode="json", exclude_none=True)

    tool_config = {}
    if has_tools:
        tool_config["tools"] = [SUMMARY_TOOL_SCHEMA]
        tool_config["tool_choice"] = "auto"

    response = client.chat.completions.create(
        messages=[system_prompt_dict] + history_dict,
        **openAI_config.model_dump(),
        **tool_config,
        # extra_body={"chat_template_kwargs": {"enable_thinking": True}},
    )
    assistant_message = response.choices[0].message
    if has_tools and assistant_message.tool_calls:
        updated_history_dict = handle_tool_calls(response, history_dict)
        final_response = client.chat.completions.create(
            messages=[system_prompt_dict] + updated_history_dict,
            **openAI_config.model_dump(),
        )
        return final_response.choices[0].message.content
    return assistant_message.content


def message_factory(input_text: str, role: Roles = Roles.USER) -> Message:
    if role is Roles.USER:
        image_contents = get_image_contents()
        if len(image_contents) > 0:
            text_content = Content(text=input_text)
            data_to_send = [text_content] + image_contents
            message = Message(role=role, content=data_to_send)
            return message
        return Message(role=role, content=input_text)
    else:
        return Message(role=role, content=input_text)
