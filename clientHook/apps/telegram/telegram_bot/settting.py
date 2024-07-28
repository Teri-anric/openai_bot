from os import getenv
from aiogram.enums import UpdateType


TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
TELEGRAM_PUBLIC_KEY = getenv("TELEGRAM_PUBLIC_KEY")

REDIS_URL = getenv("REDIS_URL")

ALLOW_UPDATES = ['message', 'my_chat_member']

