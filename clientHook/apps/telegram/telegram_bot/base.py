from aiogram import Dispatcher, Bot
from .settting import TELEGRAM_TOKEN, REDIS_URL
from .handlers import index_router
from .middleware import GetDBContextMiddleware, SaveMyMessageSessionMiddleware
from redis.asyncio.client import Redis

dp = Dispatcher()
dp.include_router(index_router)

# add middleware
dp.update.outer_middleware.register(GetDBContextMiddleware())
# add context data
if REDIS_URL:  # skip for testing
    dp["redis"] = Redis.from_url(REDIS_URL)

# skip for testing
bot: Bot = None
if TELEGRAM_TOKEN:
    bot = Bot(TELEGRAM_TOKEN)
    # add session middleware
    bot.session.middleware.register(SaveMyMessageSessionMiddleware())
