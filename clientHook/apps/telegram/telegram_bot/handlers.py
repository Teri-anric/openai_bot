from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION

from clientHook.apps.telegram.models import TelegramGroup, TelegramUser, TelegramMessages, InstructionGPT
from clientHook.apps.telegram.openai.conversation import run_conversation

from .utils import RedisQueue, get_available_functions

index_router = Router()


@index_router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def new_group_register(update: types.ChatMemberUpdated, db_group: TelegramGroup):
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
async def handled_messages(message: types.Message, message_quote: RedisQueue, db_user: TelegramUser, bot: Bot,
                           db_group: TelegramGroup = None):
    message_obj = TelegramMessages(
        message_id=message.message_id,
        user=db_user,
        group=db_group,
        text=message.text
    )
    await message_obj.asave()
    if not db_group:
        return

    gpt_instruction = await InstructionGPT.objects.aget(telegram_group=db_group)

    count = await message_quote.add(db_group.id, message_obj.message_id)
    if count < gpt_instruction.max_messages:
        return

    message_ids = await message_quote.pop(db_group.id, message_obj.message_id)
    messages = TelegramMessages.objects.select_related("user").filter(message_id__in=message_ids).all()
    await run_conversation(gpt_instruction, messages,
                           available_functions=get_available_functions(bot, message.chat.id))
