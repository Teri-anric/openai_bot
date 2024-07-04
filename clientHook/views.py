from django.http import JsonResponse, HttpResponse
from django.http import HttpRequest
from json import loads
from .telegram_bot.base import dp, bot
from .telegram_bot.utils import prepare_response
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.methods import TelegramMethod


async def telegram_webhook(request: HttpRequest):
    if request.method == "GET":
        url = request.get_host() + request.get_full_path()
        try:
            result = await bot.set_webhook(url)
        except Exception as e:
            result = str(e)
        return JsonResponse(result)

    if request.method != "POST":
        return HttpResponse(status=405)

    result = await dp.feed_raw_update(bot, loads(request.body))
    if isinstance(result, TelegramMethod):
        return await prepare_response(bot, result)

    return HttpResponse(status=200)

