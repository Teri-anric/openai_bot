from openai.types.chat.completion_create_params import Function
from openai.types.shared_params import FunctionDefinition, FunctionParameters
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam

TOOLS: list[ChatCompletionToolParam] = [
    dict(
        type="function",
        function=dict(
            name="answer",
            description="send answer to message",
            parameters=dict(
                type="object",
                required=["message_id", "text"],
                properties=dict(
                    message_id=dict(
                        type="integer",
                    ),
                    text=dict(
                        type="string"
                    ),
                )
            )
        )
    )
]
