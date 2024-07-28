from django.db.models import QuerySet
from openai import AsyncOpenAI
from typing import Callable, Awaitable
from openai.types.chat.chat_completion_message_param import ChatCompletionSystemMessageParam, ChatCompletionMessageParam
from .settings import TOOLS
from .utils import prepare_chat_messages, run_functions
import json

from clientHook.apps.telegram.models import InstructionGPT, TelegramMessages

client = AsyncOpenAI()


async def run_conversation(instruction: InstructionGPT, messages: QuerySet[TelegramMessages], available_functions: dict[str, Callable[..., Awaitable]]):
    # send the conversation and available functions to the model
    response = await client.chat.completions.create(
        model=instruction.gpt_model,
        messages=await prepare_chat_messages(instruction, messages),
        tools=TOOLS,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    await run_functions(response_message.tool_calls, available_functions=available_functions)



