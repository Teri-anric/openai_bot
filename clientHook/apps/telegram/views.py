from json import loads

from aiogram.methods import TelegramMethod
from aiogram.types import FSInputFile
from django.http import HttpRequest
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .telegram_bot.base import dp, bot
from .telegram_bot.settting import TELEGRAM_PUBLIC_KEY, ALLOW_UPDATES
from .telegram_bot.utils import prepare_response


@csrf_exempt
async def telegram_webhook(request: HttpRequest):
    """
    Handles incoming webhook requests from Telegram.

    This function sets up the webhook for the Telegram bot if the request method is GET.
    For POST requests, it processes the incoming updates and sends responses accordingly.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: The HTTP response indicating the result of the operation.
    """
    assert (
        bot is not None
    ), "Can't work telegram bot, not set `TELEGRAM_TOKEN` environments variable"

    if request.method == "GET":
        url = "https://13.49.44.45/api/telegram/"
        
        try:
            certify = None
            if TELEGRAM_PUBLIC_KEY:
                certify = FSInputFile(TELEGRAM_PUBLIC_KEY)
            result = await bot.set_webhook(
                url, certificate=certify, allowed_updates=ALLOW_UPDATES
            )
            return JsonResponse(dict(status=result))
        except Exception as e:
            return JsonResponse(dict(status=False, error_message=str(e)))
    
    if request.method != "POST":
        return HttpResponse(status=405)
    
    try:
        result = await dp.feed_raw_update(bot, loads(request.body))
        if isinstance(result, TelegramMethod):
            return await prepare_response(bot, result)
    finally:
        return HttpResponse(status=200)
