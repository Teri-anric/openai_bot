from aiogram import Router, types
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION

from clientHook.apps.telegram.models import TelegramGroup, TelegramUser, TelegramMessages, InstructionGPT

index_router = Router()


@index_router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def new_group_register(update: types.ChatMemberUpdated):
    administrators = await update.chat.get_administrators()
    admins = []
    for administrator in administrators:
        admins.append(TelegramUser(id=administrator.user.id))
    group = TelegramGroup(
        id=update.chat.id,
        title=update.chat.title,
        admins=admins,
        gpt_instruction=InstructionGPT(
            prompt_text="Help with questions in the chat."
        )
    )
    await group.asave()


@index_router.message()
async def handled_messages(message: types.Message, db_user: TelegramUser, db_group: TelegramGroup = None):
    message_obj = TelegramMessages(
        message_id=message.message_id,
        user=db_user,
        group=db_group,
        text=message.text
    )
    await message_obj.asave()
