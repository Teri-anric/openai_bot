from django.conf import settings
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam

OPENAI_API_KEY = settings.OPENAI_API_KEY

TOOLS: list[ChatCompletionToolParam] = [
    dict(
        type="function",
        function=dict(
            name="reply",
            description="send reply to message",
            parameters=dict(
                type="object",
                required=["message_id", "text"],
                properties=dict(
                    message_id=dict(
                        type="integer",
                    ),
                    text=dict(type="string"),
                ),
            ),
        ),
    ),
    dict(
        type="function",
        function=dict(
            name="answer",
            description="send text answer to chat",
            parameters=dict(
                type="object",
                required=["text"],
                properties=dict(
                    text=dict(type="string"),
                ),
            ),
        ),
    ),
]
