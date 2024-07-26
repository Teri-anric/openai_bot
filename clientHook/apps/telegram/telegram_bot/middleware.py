from contextlib import suppress
from typing import Callable, Dict, Any, Awaitable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject, User, Chat

from clientHook.apps.telegram.models import TelegramUser, TelegramGroup


class SaveUserMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        event_from_user: User | None = data.get("event_from_user", None)
        db_user = None
        if event_from_user is not None:
            db_user = TelegramUser(
                id=event_from_user.id,
                last_name=event_from_user.last_name,
                first_name=event_from_user.first_name
            )
            await db_user.asave()
        data['db_user'] = db_user
        await handler(event, data)


class GroupMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        event_from_chat: Chat | None = data.get("event_from_chat", None)
        db_group = None
        if event_from_chat is not None:
            with suppress(TelegramGroup.DoesNotExist):  # type: ignore
                db_group = await TelegramGroup.objects.aget(event_from_chat.id)
        data['db_group'] = db_group
        await handler(event, data)
