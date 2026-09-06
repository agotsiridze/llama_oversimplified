import traceback


from utils import read_system_prompt, Summary, time_tracker
from schemas import Message, Roles
from openAIchat import message_in_chat, message_factory

chat_history: list[Message] = []
MAX_MESSAGES = 100
REDUCE_BY = 30


system_prompt = read_system_prompt("/workplace/openAIchat/system_prompt.txt")
summarizer = Summary()

with time_tracker(len(chat_history)):
    initial_message = message_in_chat(system_prompt, chat_history, has_tools=True)
print(initial_message)
chat_history.append(message_factory(input_text=initial_message, role=Roles.ASSISTANT))
while True:
    try:
        input_text = input("You: ")
        if not input_text.strip():
            raise ValueError("Input cannot be empty.")

        chat_history.append(message_factory(str(input_text)))

        with time_tracker(len(chat_history)):
            response = message_in_chat(system_prompt, chat_history, has_tools=True)

            chat_history.append(
                message_factory(input_text=str(response), role=Roles.ASSISTANT)
            )

            if len(chat_history) > MAX_MESSAGES:
                summarizer.make_summary(chat_history[:REDUCE_BY])

                chat_history = chat_history[REDUCE_BY:]
            print(f"Assistant: {response}")

    except Exception as e:
        if chat_history[-1].role == Roles.USER:
            chat_history.pop()
        print(f"\n--- EXCEPTION CAUGHT ---")
        print(
            f"Type:    {type(e).__name__}"
        )
        print(f"Message: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
