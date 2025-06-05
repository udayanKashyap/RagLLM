from os import name
from django.shortcuts import render
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import DocumentSerializer
from User.llm import VectorDocument


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
