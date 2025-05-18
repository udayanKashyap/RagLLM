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
                    "uniqueItems": true,
                },
            },
            "required": ["role", "content"],
        },
    }
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, related_name="chats", unique=False
    )
    messages = models.JSONField(schema=SCHEMA)
    summary = models.CharField(max_length=500, unique=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
