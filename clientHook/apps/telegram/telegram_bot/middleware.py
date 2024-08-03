from contextlib import suppress
from typing import Callable, Dict, Any, Awaitable

from aiogram import Bot
from aiogram.client.session.middlewares.base import (
    BaseRequestMiddleware,
    NextRequestMiddlewareType,
)
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.dispatcher.middlewares.user_context import EVENT_CONTEXT_KEY, EventContext
from aiogram.methods import TelegramMethod, Response, SendMessage
from aiogram.methods.base import TelegramType
from aiogram.types import TelegramObject, Message

from clientHook.apps.telegram.models import (
    TelegramUser,
    TelegramGroup,
    TelegramMessages,
)


class GetDBContextMiddleware(BaseMiddleware):
    """
    Middleware to fetch or create TelegramUser and TelegramGroup instances from the event context.
    """

    @staticmethod
    async def get_db_user_from_context(
        event_context: EventContext,
    ) -> TelegramUser | None:
        """
        Retrieve or create a TelegramUser instance from the event context.

        :param event_context: The context of the event.
        :return: A TelegramUser instance or None if the user is not found.
        """
        if event_context.user is None:
            return None
        db_user, _ = await TelegramUser.objects.aget_or_create(
            user_id=event_context.user.id,
            last_name=event_context.user.last_name,
            first_name=event_context.user.first_name,
        )
        return db_user

    @staticmethod
    async def get_db_group_from_context(
        event_context: EventContext,
    ) -> TelegramGroup | None:
        """
        Retrieve or create a TelegramGroup instance from the event context.

        :param event_context: The context of the event.
        :return: A TelegramGroup instance or None if the group is not found.
        """
        if not event_context.chat or not event_context.chat.title:
            return
        db_group, _ = await TelegramGroup.objects.aget_or_create(
            group_id=event_context.chat_id, title=event_context.chat.title
        )
        return db_group

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Middleware call method to update the data dictionary with db_user and db_group.

        :param handler: The next handler in the middleware chain.
        :param event: The event object.
        :param data: The data dictionary.
        :return: The result of the handler.
        """
        event_context: EventContext = data.get(EVENT_CONTEXT_KEY, None)
        if event_context:
            # get user and group or update context
            data.update(
                db_user=await self.get_db_user_from_context(event_context),
                db_group=await self.get_db_group_from_context(event_context),
            )
        return await handler(event, data)


class SaveMyMessageSessionMiddleware(BaseRequestMiddleware):
    """
    Middleware to save messages sent by the bot to the database.
    """

    def __init__(self):
        """
        Initialize the middleware.
        """
        self._db_bot_user = None

    async def get_db_bot_user(self, bot: Bot):
        """
        Retrieve or create a TelegramUser instance for the bot.

        :param bot: The bot instance.
        :return: A TelegramUser instance.
        """
        if not self._db_bot_user:
            user = await bot.me()
            self._db_bot_user, _ = await TelegramUser.objects.aget_or_create(
                user_id=user.id, last_name=user.last_name, first_name=user.first_name
            )
        return self._db_bot_user

    async def save_message(self, bot: Bot, method: SendMessage, result: Message):
        """
        Save a message sent by the bot to the database.

        :param bot: The bot instance.
        :param method: The SendMessage method.
        :param result: The result of the SendMessage method.
        """
        db_bot_user = await self.get_db_bot_user(bot)
        with suppress(TelegramGroup.DoesNotExist):  # type: ignore
            db_group = await TelegramGroup.objects.aget(group_id=method.chat_id)
            # get reply message
            reply_message = None
            if method.reply_to_message_id:
                with suppress(TelegramMessages.DoesNotExist):  # type: ignore
                    reply_message = await TelegramMessages.objects.aget(
                        message_id=method.reply_to_message_id
                    )
            # create message
            db_message = TelegramMessages(
                message_id=result.message_id,
                group=db_group,
                user=db_bot_user,
                text=method.text,
                reply_to_message=reply_message,
            )
            await db_message.asave()

    async def __call__(
        self,
        make_request: NextRequestMiddlewareType[TelegramType],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> Response[TelegramType]:
        """
        Middleware call method to save messages sent by the bot to the database.

        :param make_request: The next request middleware in the chain.
        :param bot: The bot instance.
        :param method: The TelegramMethod instance.
        :return: The response from the Telegram API.
        """
        result = await make_request(bot, method)
        if isinstance(method, SendMessage):
            await self.save_message(bot, method, result)  # type: ignore
        return result
