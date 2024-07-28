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
    admins = [await TelegramUser.create_and_asave_from_telegram_user(administrator.user) for administrator in
              administrators]
    await db_group.admins.aset(admins)
    await db_group.asave(update_fields=['admins'])

    # create new instruction
    if not db_group.gpt_instruction:
        instruction_gpt = InstructionGPT()
        await instruction_gpt.asave()
        db_group.gpt_instruction = instruction_gpt
        await db_group.asave()

    return update.answer("Hi")


@index_router.message(F.text)
async def handled_messages(message: types.Message, queue: RedisQueue, db_user: TelegramUser, bot: Bot,
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

    count = await queue.add(db_group.id, message_obj.message_id)
    if count < db_group.gpt_instruction.max_messages:
        return

    message_ids = await queue.pop(db_group.id, message_obj.message_id)
    messages = await TelegramMessages.objects.aget(*message_ids)
    await run_conversation(db_group.gpt_instruction, messages,
                           available_functions=get_available_functions(bot, message.chat.id))
