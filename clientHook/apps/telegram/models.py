from django.db import models
import json
from aiogram import types as telegram_types
from django.utils import timezone


class GPTResponse(models.Model):
    text = models.TextField()

    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class TelegramUser(models.Model):
    """
    Model representing a Telegram user.

    Attributes:
        id (BigIntegerField): Unique identifier for the user.
        first_name (CharField): First name of the user.
        last_name (CharField): Last name of the user (can be null).
        created_at (DateTimeField): The date and time when the user was created.
    """

    id = models.BigIntegerField(unique=True, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True)

    created_at = models.DateTimeField(auto_now=True)


    @property
    def full_name(self):
        """
        Returns the full name of the user.

        If the last name is not provided, it returns only the first name.
        """
        if self.last_name:
            return f"{self.last_name} {self.first_name}"
        return self.first_name

    @classmethod
    def from_telegram_user(cls, user: telegram_types.User):
        return cls(
            id=user.id,
            last_name=user.last_name,
            first_name=user.first_name
        )

    def __str__(self):
        return self.full_name


class TelegramGroup(models.Model):
    """
    Model representing a Telegram group.

    Attributes:
        id (BigIntegerField): Unique identifier for the group.
        title (CharField): Title of the group.
        admins (ManyToManyField): Many-to-many relationship with TelegramUser indicating the admins of the group.
    """

    id = models.BigIntegerField(primary_key=True, unique=True)

    title = models.CharField(max_length=256)
    admins = models.ManyToManyField(TelegramUser)

    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TelegramMessages(models.Model):
    """
    Model representing a message in a Telegram group.

    Attributes:
        message_id (int): The ID of the message.
        user (TelegramUser): The user who sent the message.
        group (TelegramGroup): The group where the message was sent.
        text (str): The content of the message.
        answer(GPTResponse): answered gpt
    """

    message_id = models.BigIntegerField(null=False)
    user = models.ForeignKey(TelegramUser, null=True, on_delete=models.CASCADE)
    group = models.ForeignKey(TelegramGroup, null=True, on_delete=models.CASCADE)
    # group is null the private user chat

    created_at = models.DateTimeField(auto_now=True)

    text = models.TextField()

    answer = models.OneToOneField(GPTResponse, null=True, on_delete=models.SET_NULL)

    @property
    def is_responded(self):
        """ Indicates whether the message has been responded to. """
        return self.answer is not None

    def __str__(self):
        return f"{self.group or ''}>{self.user}: {self.text}"


class InstructionGPT(models.Model):
    prompt_text = models.TextField(default="Help with questions in the chat.")
    gpt_model = models.TextField(default="gpt-3.5-turbo")

    max_messages = models.IntegerField(default=10)
    # max_interval = models.DurationField(default=)

    telegram_group = models.OneToOneField(TelegramGroup, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.telegram_group.title}: {self.prompt_text}"
