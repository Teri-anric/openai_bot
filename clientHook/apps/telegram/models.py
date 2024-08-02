from django.db import models
from aiogram import types as telegram_types

# FIXME create base class with uuid autofield for id in all models
# FIXME you can also add `created_add` and `updated_at` fields to all models in Base models
class GPTResponse(models.Model):
    text = models.TextField()

    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # FIXME add docstring
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
    # FIXME use uuid from BaseModel for id field as uuid
    # FIXME change id to user_id it will be more clear
    # FIXME add to django admin checking if this user exist or not
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
        # FIXME add docstring and annotation type
        return cls(
            id=user.id,
            last_name=user.last_name,
            first_name=user.first_name
        )

    def __str__(self):
        # FIXME add docstring
        return self.full_name


class TelegramGroup(models.Model):
    """
    Model representing a Telegram group.

    Attributes:
        id (BigIntegerField): Unique identifier for the group.
        title (CharField): Title of the group.
        admins (ManyToManyField): Many-to-many relationship with TelegramUser indicating the admins of the group.
    """
    # FIXME use uuid from BaseModel for id field as uuid
    # FIXME change id to group_id it will be more clear
    # FIXME in django admin, add function to check if this group is exist or not
    id = models.BigIntegerField(primary_key=True, unique=True)

    title = models.CharField(max_length=256)
    admins = models.ManyToManyField(TelegramUser)
    # FIXME move this field to BaseModel to not repeat yourself
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # FIXME add docstring
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
    # FIXME BigIntegerField(null=False) null=False is default value not needed to add it here
    message_id = models.BigIntegerField(null=False)
    user = models.ForeignKey(TelegramUser, null=True, on_delete=models.CASCADE)
    group = models.ForeignKey(TelegramGroup, null=True, on_delete=models.CASCADE)
    # group is null the private user chat
    # FIXME move this field to BaseModel
    created_at = models.DateTimeField(auto_now=True)

    text = models.TextField()
    answer = models.OneToOneField(GPTResponse, null=True, on_delete=models.SET_NULL)

    @property
    def is_responded(self):
        """ Indicates whether the message has been responded to. """
        # FIXME use bool(self.answer) instead of self.answer is not None
        return self.answer is not None

    def __str__(self):
        # FIXME add docstring
        return f"{self.group or ''}>{self.user}: {self.text}"


class InstructionGPT(models.Model):
    # FIXME add docstring
    prompt_text = models.TextField(default="Help with questions in the chat.")
    # FIXME add choice list with all avaliable versions of gpt models
    # FIXME it would be nice if you can also display price for it in the admin panel
    gpt_model = models.TextField(default="gpt-3.5-turbo")
    # FIXME add max_messages_num -> <description>_<description>_<main>
    max_messages = models.IntegerField(default=10)
    # FIXME remove it if you don't use it
    # max_interval = models.DurationField(default=)

    telegram_group = models.OneToOneField(TelegramGroup, on_delete=models.CASCADE)

    def __str__(self):
        # FIXME add docstring
        return f"{self.telegram_group.title}: {self.prompt_text}"
