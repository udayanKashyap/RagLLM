import binascii
from typing import Required
from rest_framework import serializers
from .models import Document
import base64
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator


class DocumentSerializer(serializers.ModelSerializer):
    document = serializers.FileField(
        write_only=True,
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )
    content = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Document
        fields = ["id", "file", "content", "uploaded_at", "document"]
        read_only_fields = ["file", "uploaded_at"]

    def validate(self, data):
        has_pdf = "document" in data
        has_text = "content" in data  # Check the source key

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
            # Create the Document with the uploaded file
            return Document.objects.create(
                file=document_file, owned_by=user, **validated_data
            )
        elif "content" in validated_data:
            # Handle direct text input
            content = validated_data.pop("content")
            return Document.objects.create(
                content=content, owned_by=user, **validated_data
            )
        else:
            raise serializers.ValidationError("No valid data provided.")
