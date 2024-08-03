from typing import Callable, Awaitable

from django.db.models import QuerySet
from openai import AsyncOpenAI

from clientHook.apps.telegram.models import InstructionGPT, TelegramMessages
from .settings import TOOLS, OPENAI_API_KEY
from .utils import prepare_chat_messages, run_functions

# Initialize the OpenAI client if the API key is set
client: AsyncOpenAI = None
if OPENAI_API_KEY:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def run_conversation(
    instruction: InstructionGPT,
    messages: QuerySet[TelegramMessages],
    available_functions: dict[str, Callable[..., Awaitable]],
):
    """
    Runs a conversation with the OpenAI model based on the provided instruction and messages.

    This function sends the conversation and available functions to the OpenAI model,
    processes the response, and executes the necessary functions.

    Args:
        instruction (InstructionGPT): The instruction for the GPT model.
        messages (QuerySet[TelegramMessages]): The messages to be processed.
        available_functions (dict[str, Callable[..., Awaitable]]): A dictionary of available functions
            that can be called by the model.

    Raises:
        AssertionError: If the `OPENAI_API_KEY` environment variable is not set.
    """
    assert (
        OPENAI_API_KEY
    ), "Not set `OPENAI_API_KEY` environment variables, can't usage openai"

    # Send the conversation and available functions to the model
    response = await client.chat.completions.create(
        model=instruction.gpt_model,
        messages=await prepare_chat_messages(instruction, messages),
        tools=TOOLS,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )

    # Process the response message
    response_message = response.choices[0].message

    # Run the necessary functions based on the response
    await run_functions(
        response_message.tool_calls, available_functions=available_functions
    )
