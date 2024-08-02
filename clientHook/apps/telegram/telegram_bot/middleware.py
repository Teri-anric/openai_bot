from contextlib import suppress
from typing import Callable, Dict, Any, Awaitable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject, User, Chat

from clientHook.apps.telegram.models import TelegramUser, TelegramGroup

from aiogram.dispatcher.middlewares.user_context import EVENT_CONTEXT_KEY, EventContext


class GetDBContextMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        # FIXME add docstring
        event_context: EventContext = data.get(EVENT_CONTEXT_KEY, None)
        # get and save user
        # FIXME add annotation type to db_user
        db_user = None
        if event_context.user is not None:
            db_user = TelegramUser.from_telegram_user(event_context.user)
            await db_user.asave()
        # get group
        # FIXME add annotation type to db_group
        db_group = None
        if event_context.chat and event_context.chat.title:
            db_group, _ = await TelegramGroup.objects.aget_or_create(id=event_context.chat_id,
                                                                     title=event_context.chat.title)
        # update context
        data.update(db_user=db_user, db_group=db_group)
        return await handler(event, data)
