from django.http import JsonResponse, HttpResponse
from django.http import HttpRequest
from json import loads
from .telegram_bot.base import dp, bot
from .telegram_bot.utils import prepare_response
from .telegram_bot.settting import TELEGRAM_PUBLIC_KEY, ALLOW_UPDATES
from aiogram.methods import TelegramMethod
from aiogram.types import FSInputFile
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
async def telegram_webhook(request: HttpRequest):
    # FIXME add docstring
    if request.method == "GET":
        url = request.get_host() + request.get_full_path()
        try:
            certify = None
            if TELEGRAM_PUBLIC_KEY:
                certify = FSInputFile(TELEGRAM_PUBLIC_KEY)
            result = await bot.set_webhook(url, certificate=certify,
                                           allowed_updates=ALLOW_UPDATES)
            return JsonResponse(dict(status=result))
        except Exception as e:
            return JsonResponse(dict(status=False, error_message=str(e)))

    if request.method != "POST":
        return HttpResponse(status=405)

    result = await dp.feed_raw_update(bot, loads(request.body))
    if isinstance(result, TelegramMethod):
        return await prepare_response(bot, result)

    return HttpResponse(status=200)
