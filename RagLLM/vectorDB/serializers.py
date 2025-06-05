import binascii
from typing import Required
from rest_framework import serializers
from .models import Document
import base64
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator


class DocumentSerializer(serializers.ModelSerializer):
    document = serializers.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        write_only=True,  # Only used for input, not returned in response
    )
    content = serializers.CharField(required=False)
    file_name = serializers.CharField(read_only=True)
    file_size = serializers.IntegerField(read_only=True)

    class Meta:
        model = Document
        fields = ["id", "file_name", "file_size", "content", "uploaded_at", "document"]
        read_only_fields = ["file_name", "file_size", "uploaded_at"]

    def validate(self, data):
        has_pdf = "document" in data
        has_text = "content" in data
        if not has_pdf and not has_text:
            raise serializers.ValidationError(
                "Document or extracted text must be provided."
            )
        return data

    def create(self, validated_data):
        user = self.context["request"].user

        if "document" in validated_data:
            # Handle PDF file upload
            document_file = validated_data.pop("document")

            # Automatically extract file information
            file_data = document_file.read()
            file_name = document_file.name
            file_size = len(file_data)

            # Create the Document with automatically extracted file info
            return Document.objects.create(
                file_data=file_data,
                file_name=file_name,
                file_size=file_size,
                owned_by=user,
                **validated_data,
            )
        elif "content" in validated_data:
            # Handle direct text input (no file info needed)
            content = validated_data.pop("content")
            return Document.objects.create(
                content=content, owned_by=user, **validated_data
            )
        else:
            raise serializers.ValidationError("No valid data provided.")
