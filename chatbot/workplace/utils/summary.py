from time import sleep

from openai import OpenAI

from schemas import Message, Roles, Content
from config import OpenAIConfig


class Summary:
    summary = """

    """

    client = OpenAI(base_url="http://llama_cpp_server:8081/v1", api_key="none")
    openAI_config = OpenAIConfig(temperature=0.1)

    summary_system_prompt: Message = Message(
        role=Roles.SYSTEM,
        content=[
            Content(
                text="make a summary of chat. keep in mind facts that changed and what is important for model to know for keeping the conversation, keep it under 500 words and mostly facts and changes, use previous summary provided by assistant as well."
            )
        ],
    )

    @staticmethod
    def stringify_history(msg: Message) -> str:
        author, text = msg.role.value, msg.content
        message_str = f"{author} - {text}"
        return message_str

    def make_summary(self, history: list[Message]) -> None:
        chat = [self.stringify_history(msg) for msg in history]
        chat_history_str = "\n".join(chat)
        chat_for_summary = [Message(content=chat_history_str)]
        history_dict = [
            msg.model_dump(mode="json", exclude_none=True) for msg in chat_for_summary
        ]
        sleep(3)

        response = self.client.chat.completions.create(
            messages=[
                self.summary_system_prompt.model_dump(mode="json", exclude_none=True)
            ]
            + history_dict,
            **self.openAI_config.model_dump(),
        )

        self.summary = "SUMMARY: \n" + response.choices[0].message.content
        print("^" * 20)
        print(self.summary)
        print("^" * 20)
        sleep(3)

    def read_context(self) -> str:
        """
        Retrieves the long-term summary context containing archived chat history,
        user preferences, and persistent facts from previous turns of the conversation.
        Call this tool if the user asks about older topics not present in the current chat.
        """

        if not self.summary:
            return """
                There is no long-term archived summary yet because the conversation
                is still fresh and entirely present within the active chat window.
                Please rely on the current visible message history to answer the user.
                """

        return self.summary
