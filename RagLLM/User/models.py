import json
from enum import unique
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password, name=None):
        if not email:
            raise ValueError("error: email is mandatory")

        user = self.model(name=name, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    name = models.CharField(max_length=100, unique=False, blank=True)
    email = models.EmailField(max_length=100, unique=True, blank=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return f"{self.email} - {self.email}"


class Folder(models.Model):
    owned_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="folders", unique=False
    )
    name = models.CharField(max_length=100, unique=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Folder - name: {self.name}, owner: {self.owned_by}"


class Chat(models.Model):
    SCHEMA = {
        "title": "Chat Message Schema",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "role": {"type": "string"},
                "content": {"type": "string", "minLength": 1},
                "documents": {
                    "type": "array",
                    "items": {
                        "type": "integer",
                        "minimum": 0,
                    },
                },
            },
            "required": ["role", "content"],
        },
    }
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, related_name="chats", unique=False
    )
    summary = models.CharField(max_length=500, unique=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    messages = models.JSONField()  # Remove schema parameter

    def clean(self):
        super().clean()
        self.validate_messages_schema()

    def validate_messages_schema(self):
        from jsonschema import validate, ValidationError

        try:
            validate(instance=self.messages, schema=self.SCHEMA)
        except ValidationError as e:
            raise ValidationError(f"Messages don't match schema: {e.message}")

    def save(self, *args, **kwargs):
        self.full_clean()  # Runs clean() and validators
        super().save(*args, **kwargs)
