from contextlib import suppress
from typing import Callable, Dict, Any, Awaitable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject, User, Chat

from clientHook.apps.telegram.models import TelegramUser, TelegramGroup

from aiogram.dispatcher.middlewares.user_context import EVENT_CONTEXT_KEY, EventContext


class GetDBContextMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        event_context: EventContext = data.get(EVENT_CONTEXT_KEY, None)
        # get and save user
        db_user = None
        if event_context.user is not None:
            db_user = TelegramUser.from_telegram_user(event_context.user)
            await db_user.asave()
        # get group
        db_group = None
        if event_context.chat is not None:
            db_group = TelegramGroup(id=event_context.chat_id, title=event_context.chat.title)
            await db_group.asave(update_fields=['title'])
        # update context
        data.update(db_user=db_user, db_group=db_group)
        return await handler(event, data)
