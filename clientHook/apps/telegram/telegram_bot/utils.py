import secrets
from typing import Dict

from aiogram import Bot
from aiogram.methods import TelegramMethod
from aiogram.types import InputFile
from aiohttp import MultipartWriter

from django.http import HttpResponse
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from redis.asyncio import Redis


async def prepare_response(bot: Bot, result: TelegramMethod = None) -> HttpResponse:
    boundary = f"webhookBoundary{secrets.token_urlsafe(16)}"
    response = HttpResponse(content_type=f'multipart/form-data; boundary={boundary}')
    if not result:
        return response

    response.write(f'--{boundary}\r\n')
    response.write(f'Content-Disposition: form-data; name="method"\r\n\r\n')
    response.write(f'{result.__api_method__}\r\n')

    files: Dict[str, InputFile] = {}

    for key, value in result.model_dump(warnings=False).items():
        value = bot.session.prepare_value(value, bot, files)
        if not value:
            continue

        response.write(f'--{boundary}\r\n')
        response.write(f'Content-Disposition: form-data; name="{key}"\r\n\r\n')
        response.write(f'{value}\r\n')

    for key, value in files.items():
        response.write(f'--{boundary}\r\n')
        response.write(f'Content-Disposition: form-data; name="{key}"; filename="{value.filename or key}"\r\n')
        # response.write(f'Content-Type: {value.content_type}\r\n\r\n')
        async for chunk in value.read(bot):
            response.write(chunk)
        response.write('\r\n')

    response.write(f'--{boundary}--\r\n')

    return response


class RedisQueue:
    def __init__(self, redis_url='redis://localhost', key: str = None):
        self.redis_url = redis_url
        self.key = key or "queue"
        self.redis = Redis.from_url(self.redis_url)

    def _get_group_key(self, group_id: int):
        return f"{self.key}:{group_id}"

    async def add(self, group_id: int, message_id: int) -> int:
        async with self.redis as client:
            return await client.lpush(self._get_group_key(group_id), message_id)

    async def pop(self, group_id: int, count: int) -> list[int]:
        async with self.redis as client:
            queue_key = self._get_group_key(group_id)
            messages = await self.redis.rpop(queue_key, count=count)
            return messages


def get_available_functions(bot: Bot, chat_id: int):
    async def answer(message_id: int, text: str):
        await bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=message_id)

    return {
        "answer": answer
    }