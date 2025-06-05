from os import name
from django.shortcuts import render
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import DocumentSerializer
from User.llm import VectorDocument
from .models import Document


# Create your views here.


class CreateDocumentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = DocumentSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            # vectorDB = VectorDocument(
            #     id=serializer.instance.id,
            #     name=serializer.instance.file_name,  # Updated to use file_name
            #     content=serializer.instance.content,
            # )
            # vectorDB.createEmbedding()
            # vectorDB.storeEmbedding()
            return Response(
                {
                    "id": serializer.instance.id,
                    "file_name": serializer.instance.file_name,
                    "file_size": serializer.instance.file_size,
                    "message": "Document created successfully",
                },
                status=201,
            )
        return Response(serializer.errors, status=400)


class GetDocumentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        documents = Document.objects.filter(owned_by=request.user)
        data = [
            {
                "id": doc.id,
                "file_name": doc.file_name,
                "file_size": doc.file_size,
                "uploaded_at": doc.uploaded_at,
            }
            for doc in documents
        ]
        return Response(data, status=200)
