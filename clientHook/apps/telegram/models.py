from uuid import uuid4

from aiogram import types as telegram_types
from django.db import models


class BaseModel(models.Model):
    """
    Abstract model class that provides common fields and functionality

    Attributes:
        id (UUIDField): The primary key for the model.
        created_at (DateTimeField): The date and time when the record was created.
        updated_at (DateTimeField): The date and time when the record was last updated.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TelegramUser(BaseModel):
    """
    Model representing a Telegram user.

    Attributes:
        user_id (BigIntegerField): Unique identifier for the telegram user.
        first_name (CharField): First name of the user.
        last_name (CharField): Last name of the user (can be null).
    """

    user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True)

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
        """
        Create an instance of TelegramUser from a Telegram User object.

        Args:
            user (TelegramUser): A Telegram User object.

        Returns:
            TelegramUser: An instance of YourModel populated with data from the Telegram User object.
        """
        return cls(
            user_id=user.id, last_name=user.last_name, first_name=user.first_name
        )

    def __str__(self):
        """
        Returns the string representation of the model instance.

        Returns:
            str: The full name of the user.
        """
        return self.full_name


class TelegramGroup(BaseModel):
    """
    Model representing a Telegram group.

    Attributes:
        group_id (BigIntegerField): Unique identifier for the telegram group.
        title (CharField): Title of the group.
        admins (ManyToManyField): Many-to-many relationship with TelegramUser indicating the admins of the group.
    """

    group_id = models.BigIntegerField(unique=True)

    title = models.CharField(max_length=256)
    admins = models.ManyToManyField(TelegramUser)

    def __str__(self):
        """
        Returns the string representation of the model instance.

        Returns:
            str: The title of the model instance.
        """
        return self.title


class TelegramMessages(BaseModel):
    """
    Model representing a message in a Telegram group.

    Attributes:
        message_id (int): The ID of the message.
        user (TelegramUser): The user who sent the message.
        group (TelegramGroup): The group where the message was sent.
        text (str): The content of the message.
        reply_to_message (TelegramMessages): A reference to another message that this message is replying to.
    """

    message_id = models.BigIntegerField()
    user = models.ForeignKey(TelegramUser, null=True, on_delete=models.CASCADE)
    group = models.ForeignKey(TelegramGroup, null=True, on_delete=models.CASCADE)
    # group is null the private user chat

    text = models.TextField()
    reply_to_message = models.ForeignKey(
        "self", null=True, on_delete=models.SET_NULL, related_name="replies"
    )

    def __str__(self):
        """
        Returns the string representation of the Telegram message instance.

        Returns:
            str: A string representing the message, including the group (if available), user, and the message text.
        """
        return f"{self.group or ''}>{self.user}: {self.text}"


class InstructionGPT(BaseModel):
    """
    Model representing GPT instructions and configuration for a Telegram group.

    Attributes:
        prompt_text (str): The prompt text used for generating GPT responses.
        gpt_model (str): The GPT model version used (e.g., 'gpt-3.5-turbo').
        trigger_message_count (int): The number of messages required to trigger the GPT response.
        context_message_count (int): The number of messages to include in the context for the GPT response.
        telegram_group (TelegramGroup): The Telegram group associated with this configuration.
    """

    GPT_MODEL_CHOICES = [
        ("gpt-4o", "GPT-4o $5/$15"),
        ("gpt-4o-2024-05-13", "GPT-4o-2024-05-13 $5/$15"),
        ("gpt-4o-mini", "GPT-4o-mini $0.15/$0.6"),
        ("gpt-4o-mini-2024-07-18", "GPT-4o-mini-2024-07-18 $0.15/$0.6"),
        ("gpt-4-turbo", "GPT-4-turbo $10/$30"),
        ("gpt-4-turbo-2024-04-09", "GPT-4-turbo-2024-04-09 $10/$30"),
        ("gpt-4-0125-preview", "GPT-4-0125-preview $10/$30"),
        ("gpt-4-turbo-preview", "GPT-4-turbo-preview $10/$30"),
        ("gpt-4-1106-preview", "GPT-4-1106-preview $10/$30"),
        ("gpt-4-vision-preview", "GPT-4-vision-preview $10/$30"),
        ("gpt-4", "GPT-4 $30/$60"),
        ("gpt-4-0314", "GPT-4-0314 $30/$60"),
        ("gpt-4-0613", "GPT-4-0613 $30/$60"),
        ("gpt-4-32k", "GPT-4-32k $60/$120"),
        ("gpt-4-32k-0314", "GPT-4-32k-0314 $60/$120"),
        ("gpt-4-32k-0613", "GPT-4-32k-0613 $60/$120"),
        ("gpt-3.5-turbo", "GPT-3.5-turbo $0.5/$1.5"),
        ("gpt-3.5-turbo-0301", "GPT-3.5-turbo-0301 $1.5/$2"),
        ("gpt-3.5-turbo-0613", "GPT-3.5-turbo-0613 $1.5/$2"),
        ("gpt-3.5-turbo-1106", "GPT-3.5-turbo-1106 $1/$2"),
        ("gpt-3.5-turbo-0125", "GPT-3.5-turbo-0125 $0.5/$1.5"),
        ("gpt-3.5-turbo-16k", "GPT-3.5-turbo-16k $3/$4"),
        ("gpt-3.5-turbo-16k-0613", "GPT-3.5-turbo-16k-0613 $3/$4"),
    ]

    gpt_model = models.CharField(choices=GPT_MODEL_CHOICES, default="gpt-3.5-turbo")
    prompt_text = models.TextField(default="Help with questions in the chat.")

    trigger_message_count = models.IntegerField(default=5)
    context_message_count = models.IntegerField(default=10)

    telegram_group = models.OneToOneField(TelegramGroup, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """
        Returns the string representation of the InstructionGPT instance.

        Returns:
            str: A string representing the Telegram group title and prompt text.
        """
        return f"{self.telegram_group.title}: {self.prompt_text}"
