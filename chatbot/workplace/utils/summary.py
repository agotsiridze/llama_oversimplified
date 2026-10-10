from openai import OpenAI

from config import OpenAIConfig
from schemas import Content, Message, Roles

SUMMARY_INSTRUCTIONS = (
    "make a summary of chat. keep in mind facts that changed and what is important "
    "for model to know for keeping the conversation, keep it under 500 words and "
    "mostly facts and changes. If a 'Previous summary' section is given, merge it "
    "with the new messages instead of dropping it."
)


class Summary:
    client = OpenAI(base_url="http://llama_cpp_server:8081/v1", api_key="none")
    openAI_config = OpenAIConfig(temperature=0.1, max_tokens=1500)
    summary_system_prompt: Message = Message(
        role=Roles.SYSTEM, content=[Content(text=SUMMARY_INSTRUCTIONS)]
    )

    def __init__(self) -> None:
        self.summary: str = ""  # empty means "no summary yet"

    def reset(self) -> None:
        self.summary = ""

    @staticmethod
    def stringify_history(msg: Message) -> str:
        return f"{msg.role.value} - {msg.text}"  # text only, no base64 images

    def make_summary(self, history: list[Message]) -> None:
        transcript = "\n".join(self.stringify_history(m) for m in history)
        if self.summary:
            transcript = (
                f"Previous summary:\n{self.summary}\n\nNew messages:\n{transcript}"
            )
        messages = [
            self.summary_system_prompt.model_dump(mode="json", exclude_none=True),
            Message(content=transcript).model_dump(mode="json", exclude_none=True),
        ]
        response = self.client.chat.completions.create(
            messages=messages,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
            **self.openAI_config.model_dump(),
        )
        self.summary = "SUMMARY: \n" + (response.choices[0].message.content or "")

    def read_context(self) -> str:
        """Long-term summary of archived chat history, read by the read_context tool."""
        if not self.summary:
            return (
                "There is no long-term archived summary yet because the conversation "
                "is still fresh and entirely present within the active chat window. "
                "Please rely on the current visible message history to answer the user."
            )
        return self.summary
