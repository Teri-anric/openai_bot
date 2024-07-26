import secrets
from typing import Dict

from aiogram import Bot
from aiogram.methods import TelegramMethod
from aiogram.types import InputFile
from aiohttp import MultipartWriter

from django.http import HttpResponse
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings


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

