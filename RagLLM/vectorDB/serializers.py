import binascii
from typing import Required
from rest_framework import serializers
from .models import Document
import base64
from django.core.files.base import ContentFile


class DocumentSerializer(serializers.ModelSerializer):
    document = serializers.CharField(write_only=True, required=False)
    filename = serializers.CharField(write_only=True, required=False)
    extractedText = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Document
        fields = ["id", "file", "extracted_text", "uploaded_at", "document", "filename"]
        read_only_fields = ["file", "uploaded_at"]

    def validate(self, data):
        has_pdf = "document" in data
        has_text = "extracted_text" in data

        if not has_pdf and not has_text:
            raise serializers.ValidationError("Error... No Data Provided")

        return data

    def create(self, validated_data):
        if "document" in validated_data:
            document = validated_data.pop("document")
            filename = validated_data.pop("document")

            try:
                decoded = base64.decode(document)
            except (TypeError, binascii.Error):
                raise serializers.ValidationError("Invalid base64 encoding")

            file = ContentFile(decoded, name=filename)
            return Document.objects.create(file=file)

        extractedText = validated_data.pop("extracted_text")
        return Document.objects.create(extracted_text=extractedText)
