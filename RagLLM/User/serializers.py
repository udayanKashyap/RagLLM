import email
from rest_framework import serializers
from .models import User, Folder, Chat
import jsonschema
from jsonschema import ValidationError, validate


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "name", "password"]
        extra_kwargs = {"email": {"required": True}, "password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name"),
        )


class FolderSerializer(serializers.ModelSerializer):
    owned_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Folder
        fields = ["id", "owned_by", "name", "created_at", "modified_at"]
        read_only_fields = ["created_at", "modified_at"]


class ChatSerializer(serializers.ModelSerializer):
    folder = serializers.PrimaryKeyRelatedField(
        queryset=Folder.objects.all(),
    )

    class Meta:
        model = Chat
        fields = ["id", "folder", "messages", "summary", "created_at", "modified_at"]
        read_only_fields = ["created_at", "modified_at"]

    def validate_messages(self, value):
        schema = Chat.SCHEMA
        try:
            for message in value:
                validate(instance=message, schema=schema["items"])
        except jsonschema.exceptions.ValidationError as e:
            raise serializers.ValidationError(f"Invalid message format: {e.message}")
        return value

    def validate_folder(self, value):
        user = self.context["request"].user
        if value.owned_by != user:
            raise serializers.ValidationError("You don't own this folder")
        return value


class MessageSerializer(serializers.Serializer):
    role = serializers.CharField()
    content = serializers.CharField()
    documents = serializers.ListField(
        child=serializers.IntegerField(min_value=0), required=False, default=[]
    )

    def validate_role(self, value):
        if value not in ["user", "system"]:
            raise serializers.ValidationError("Invalid Role")
        return value
