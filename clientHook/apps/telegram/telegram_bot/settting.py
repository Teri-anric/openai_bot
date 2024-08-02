from os import getenv

# FIXME move it to django settings, to not have credentials in different places
TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
TELEGRAM_PUBLIC_KEY = getenv("TELEGRAM_PUBLIC_KEY")

REDIS_URL = getenv("REDIS_URL")

ALLOW_UPDATES = ['message', 'my_chat_member']

