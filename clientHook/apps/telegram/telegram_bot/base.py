from aiogram import Dispatcher, Bot
from .settting import TELEGRAM_TOKEN, REDIS_URL
from .handlers import index_router
from .middleware import GetDBContextMiddleware
from .utils import RedisQueue


dp = Dispatcher()
dp.include_router(index_router)
# add middleware and context data
dp.update.outer_middleware.register(GetDBContextMiddleware())
dp["message_quote"] = RedisQueue(REDIS_URL, key="message_quote")
# skip for testing
bot: Bot = None
if TELEGRAM_TOKEN:
    bot = Bot(TELEGRAM_TOKEN)



