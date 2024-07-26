from aiogram import Dispatcher, Bot
from .settting import TELEGRAM_TOKEN
from .handlers import index_router
from .middleware import GroupMiddleware, SaveUserMiddleware

dp = Dispatcher()
dp.include_router(index_router)
dp.update.outer_middleware.register(GroupMiddleware())
dp.update.outer_middleware.register(SaveUserMiddleware())
# skip for testing
bot: Bot = None
if TELEGRAM_TOKEN:
    bot = Bot(TELEGRAM_TOKEN)



