from aiogram import Router, types, F, Bot
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION
from redis.asyncio import Redis

from clientHook.apps.telegram.models import (
    TelegramGroup,
    TelegramUser,
    TelegramMessages,
    InstructionGPT,
)
from clientHook.apps.telegram.openai.conversation import run_conversation

from .utils import get_available_functions

index_router = Router()


@index_router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def new_group_register(update: types.ChatMemberUpdated, db_group: TelegramGroup):
    """
    Handles the event when a new group is registered.

    This function fetches the list of administrators in the group, saves them to the database,
    creates a new instruction for the group, and sends a greeting message.

    Args:
        update (types.ChatMemberUpdated): The update object containing information about the group.
        db_group (TelegramGroup): The database representation of the group.
    """
    # Fetch admin list
    administrators = await update.chat.get_administrators()

    # Save admins
    admins = []
    for administrator in administrators:
        user = TelegramUser.from_telegram_user(administrator.user)
        await user.asave()
        admins.append(user)
    await db_group.admins.aset(admins)
    await db_group.asave()

    # create new instruction
    await InstructionGPT.objects.aget_or_create(telegram_group=db_group)

    return update.answer("Hi")


@index_router.message(F.text)
async def handled_messages(
    message: types.Message,
    db_user: TelegramUser,
    bot: Bot,
    db_group: TelegramGroup = None,
    redis: Redis = None,
):
    """
    Handles incoming messages and processes them according to the group's instruction.

    This function saves the incoming message to the database, checks if the message count
    triggers a conversation with the GPT model, and runs the conversation if the condition is met.

    Args:
        message (types.Message): The incoming message object.
        redis (Redis): The Redis client for caching.
        db_user (TelegramUser): The database representation of the user who sent the message.
        bot (Bot): The bot instance.
        db_group (TelegramGroup, optional): The database representation of the group. Defaults to None.
    """
    message_obj = TelegramMessages(
        message_id=message.message_id, user=db_user, group=db_group, text=message.text
    )
    await message_obj.asave()
    if not db_group:
        return
    if not redis:
        raise Warning("Not set `REDIS_URL` can't usage count trigger")

    # test count message trigger
    gpt_instruction: InstructionGPT = await InstructionGPT.objects.aget(
        telegram_group=db_group
    )
    async with redis:
        message_count_group_key = f"message_count:{db_group.group_id}"
        message_count = await redis.incr(message_count_group_key)
        if message_count < gpt_instruction.trigger_message_count:
            return
        await redis.decrby(
            message_count_group_key, gpt_instruction.trigger_message_count
        )

    messages = (
        TelegramMessages.objects.select_related(
            "user", "reply_to_message", "reply_to_message__user"
        )
        .filter(group=db_group, created_at__lte=message_obj.created_at)
        .order_by("-created_at")[: gpt_instruction.context_message_count]
    )

    await run_conversation(
        gpt_instruction,
        messages,
        available_functions=get_available_functions(bot, message.chat.id),
    )
