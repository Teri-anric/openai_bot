from aiogram import Dispatcher, Bot
from .settting import TELEGRAM_TOKEN
from .handlers import index_router

dp = Dispatcher()
dp.include_router(index_router)
# skip for testing
bot: Bot = None
if TELEGRAM_TOKEN:
    bot = Bot(TELEGRAM_TOKEN)



