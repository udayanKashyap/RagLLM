import uuid
from datetime import datetime
from pprint import pprint
import json
from django.http import StreamingHttpResponse
from http import client
import os
from PIL.Image import new
from django.http import Http404
from rest_framework.views import APIView, Response
from django.shortcuts import render
from rest_framework import serializers, status, permissions
from .serializers import (
    ChatSerializer,
    FolderSerializer,
    MessageSerializer,
    UserSerializer,
    ChatListSerializer,
)
from .models import Folder, User, Chat

from RagLLM import geminiClient
from google import genai


# Create your views here.
class UploadMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_chat(self, chatId):
        try:
            chat = Chat.objects.select_related("folder").get(pk=chatId)
            if chat.folder.owned_by != self.request.user:
                raise Http404
            return chat
        except Chat.DoesNotExist:
            raise Http404

    def post(self, request, chatId):
        chat = self.get_chat(chatId)
        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        new_message = {
            "role": serializer.validated_data["role"],
            "content": serializer.validated_data["content"],
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
        }
        messages = chat.messages or []
        messages.append(new_message)
        chat.messages = messages
        chat.save()
        pprint(messages)

        # Build the entire conversation history to pass to gemini
        conversation = []
        for msg in messages:
            # Convert to Gemini's role format (user/model)
            role = "user" if msg["role"] == "user" else "model"
            conversation.append({"role": role, "parts": [{"text": msg["content"]}]})

        def gemini_stream_generator():
            response = geminiClient.models.generate_content_stream(
                model=os.getenv("GEMINI_MODEL"),
                contents=conversation,
            )
            full_response = []
            for chunk in response:
                if chunk.text:
                    # Stream token to client
                    data = json.dumps({"token": chunk.text})
                    yield f"data: {data}\n\n"
                    full_response.append(chunk.text)

            # Save complete assistant response to chat
            assistant_message = {
                "role": "model",
                "content": "".join(full_response),
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat(),
            }
            messages.append(assistant_message)
            chat.messages = messages
            chat.save()
            yield "event: end\ndata: stream_complete\n\n"

        return StreamingHttpResponse(
            gemini_stream_generator(), content_type="text/event-stream"
        )


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            Folder.objects.create(name="Untitled", owned_by=user)

            return Response(
                {
                    "user": UserSerializer(user).data,
                    "message": "User created successfully",
                },
                status=201,
            )
        return Response(serializer.errors, status=400)


class CreateFolderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        folders = Folder.objects.filter(owned_by=request.user)
        serializer = FolderSerializer(folders, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = FolderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owned_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ModifyFolderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_folder(self, id):
        try:
            return Folder.objects.get(pk=id, owned_by=self.request.user)
        except Folder.DoesNotExist:
            raise Http404

    def put(self, request, id):
        folder = self.get_folder(id=id)
        serializer = FolderSerializer(folder, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        folder = self.get_folder(id=id)
        folder.delete()
        return Response({"message": "Folder deleted successfully"}, status=200)


class CreateChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # Get all chats of a folder
    def get(self, request, folderId):
        # Validate folder ownership
        try:
            folder = Folder.objects.get(id=folderId, owned_by=request.user)
        except Folder.DoesNotExist:
            return Response(
                {"detail": "Folder not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get chats and serialize without messages
        chats = Chat.objects.filter(folder=folder)
        serializer = ChatListSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Create a chat
    def post(self, request):
        serializer = ChatSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ModifyChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        print(id)
        try:
            chat = Chat.objects.select_related("folder").get(pk=id)
            if chat.folder.owned_by != self.request.user:
                raise Http404
            return chat
        except Chat.DoesNotExist:
            raise Http404

    # Get specific chat
    def get(self, request, id):
        chat = self.get_object(id)
        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=200)

    def patch(self, request, id):
        chat = self.get_object(id)
        serializer = ChatSerializer(
            chat, data=request.data, partial=True, context={"request": request.data}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    # delete specific chat
    def delete(self, request, id):
        chat = self.get_object(id)
        chat.delete()
        return Response({"message": "chat deleted successfully"}, status=200)


# class UploadMessageView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_chat(self, chatId):
#         try:
#             chat = Chat.objects.select_related("folder").get(pk=chatId)
#             if chat.folder.owned_by != self.request.user:
#                 raise Http404
#             return chat
#         except Chat.DoesNotExist:
#             raise Http404
#
#     def post(self, request, chatId):
#         chat = self.get_chat(chatId)
#         serializer = MessageSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=400)
#
#         newMessage = MessageSerializer.validated_data
#         messages = chat.messages or []
#         messages.append(newMessage)
#
#         chat.messages = messages
#         chat.save()
#
#         return Response(ChatSerializer(chat).data, status=200)
