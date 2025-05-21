from django.http import Http404, Http401
from rest_framework.views import APIView, Response
from django.shortcuts import render
from rest_framework import status, permissions
from .serializers import (
    ChatSerializer,
    FolderSerializer,
    MessageSerializer,
    UserSerializer,
)
from .models import Folder, User


# Create your views here.
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

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

    def post(self, request):
        serializer = ChatSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ModifyChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        try:
            chat = Chat.objects.select_related("folder").get(pk=id)
            if chat.folder.owned_by != self.request.user:
                raise Http401
            return chat
        except Chat.DoesNotExist:
            raise Http404

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

    def delete(self, request, id):
        chat = self.get_object(id)
        chat.delete()
        return Response({"message": "chat deleted successfully"}, status=200)


class UploadMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_chat(self, chatId):
        try:
            chat = Chat.objects.select_related("folder").get(pk=chatId)
            if chat.folder.owned_by != self.request.user:
                raise Http401
            return chat
        except Chat.DoesNotExist:
            raise Http404

    def post(self, request, chatId):
        chat = self.get_chat(chatId)
        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        newMessage = MessageSerializer.validated_data
        messages = chat.messages or []
        messages.append(newMessage)

        chat.messages = messages
        chat.save()

        return Response(ChatSerializer(chat).data, status=200)
