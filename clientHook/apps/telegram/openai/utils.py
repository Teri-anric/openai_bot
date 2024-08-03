import json
from typing import Callable, Awaitable, List, Dict

from django.db.models import QuerySet
from openai.types.chat import ChatCompletionMessageToolCall
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionAssistantMessageParam,
)

from clientHook.apps.telegram.models import InstructionGPT, TelegramMessages
from clientHook.apps.telegram.telegram_bot.base import bot


def _message_to_dict(message: TelegramMessages, include_reply: bool = True) -> dict:
    """
    Convert a TelegramMessages object to a dictionary.

    Args:
        message (TelegramMessages): The message object to convert.
        include_reply (bool, optional): Whether to include the reply_to_message. Defaults to True.

    Returns:
        dict: The message object as a dictionary.
    """
    return dict(
        message_id=message.message_id,
        text=message.text,
        user=(
            None
            if not message.user
            else dict(user_id=message.user.user_id, full_name=message.user.full_name)
        ),
        reply_to_message=(
            None
            if not message.reply_to_message or not include_reply
            else _message_to_dict(message.reply_to_message, False)
        ),
    )


def _prepare_message(message: TelegramMessages) -> ChatCompletionMessageParam:
    """
    Prepare a message for chat completion based on its sender.

    Args:
        message (TelegramMessages): The message object to prepare.

    Returns:
        ChatCompletionMessageParam: The prepared message for chat completion.
    """
    if bot and message.user.user_id == bot.id:
        return ChatCompletionAssistantMessageParam(
            content=json.dumps(_message_to_dict(message)), role="assistant"
        )
    return ChatCompletionUserMessageParam(
        content=json.dumps(_message_to_dict(message)),
        role="user",
        name="anonymous" if not message.user else str(message.user.user_id),
    )


async def prepare_chat_messages(
    instruction: InstructionGPT, tg_messages: QuerySet[TelegramMessages]
) -> list[ChatCompletionMessageParam]:
    """
    Prepare a list of chat messages for chat completion, including an instruction.

    Args:
        instruction (InstructionGPT): The instruction to include in the messages.
        tg_messages (QuerySet[TelegramMessages]): The queryset of TelegramMessages to prepare.

    Returns:
        list[ChatCompletionMessageParam]: The list of prepared messages for chat completion.
    """
    messages = []
    async for tg_message in tg_messages:
        messages.append(_prepare_message(tg_message))
    # Add instruction
    messages.append(
        ChatCompletionSystemMessageParam(content=instruction.prompt_text, role="system")
    )
    messages.reverse()
    return messages


async def run_functions(
    tool_calls: List[ChatCompletionMessageToolCall] | None,
    available_functions: Dict[str, Callable[..., Awaitable]],
) -> None:
    """
    Asynchronously run functions based on the tool calls provided.

    Args:
        tool_calls (List[ChatCompletionMessageToolCall] | None): A list of tool calls to execute.
        available_functions (Dict[str, Callable[..., Awaitable]]): A dictionary mapping function names to callable functions.

    Returns:
        None
    """
    # Step 1: Check if the model wanted to call a function
    if not tool_calls:
        return

    # Step 2: Send the info for each function call
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        # Get and call function
        function_to_call = available_functions.get(function_name)
        if not function_to_call:
            continue

        await function_to_call(**function_args)
