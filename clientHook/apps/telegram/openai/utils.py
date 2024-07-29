import json
from typing import Callable, Awaitable

from django.db.models import QuerySet
from openai.types.chat import ChatCompletionMessageToolCall
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam, \
    ChatCompletionMessageParam

from clientHook.apps.telegram.models import InstructionGPT, TelegramMessages


async def prepare_chat_messages(instruction: InstructionGPT, tg_messages: QuerySet[TelegramMessages]) -> list[ChatCompletionMessageParam]:
    messages = [
        ChatCompletionSystemMessageParam(
            content=instruction.prompt_text,
            role="system"
        )
    ]
    async for tg_message in tg_messages:
        messages.append(
            ChatCompletionUserMessageParam(
                content=json.dumps(dict(
                    message_id=tg_message.message_id,
                    text=tg_message.text,
                    full_name_user=None if not tg_message.user else tg_message.user.full_name
                ), ensure_ascii=False),
                role="user",
                name="anonymous" if not tg_message.user else str(tg_message.user.id)
            )
        )
    return messages


async def run_functions(tool_calls: list[ChatCompletionMessageToolCall] | None,
                        available_functions: dict[str, Callable[..., Awaitable]]):
    # Step 1: check if the model wanted to call a function
    if not tool_calls:
        return
    # Step 2: send the info for each function call
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        # Get and call function
        function_to_call = available_functions.get(function_name)
        if not function_to_call:
            continue
        await function_to_call(**function_args)
