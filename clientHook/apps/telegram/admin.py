from django.contrib import admin
from .models import TelegramUser, TelegramGroup, InstructionGPT, TelegramMessages, GPTResponse

admin.site.register([
    TelegramUser, TelegramGroup, TelegramMessages,
    InstructionGPT, GPTResponse
])

