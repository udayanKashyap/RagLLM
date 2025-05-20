from django.http import Http404
from rest_framework.views import APIView, Response
from django.shortcuts import render
from rest_framework import status, permissions
from .serializers import FolderSerializer, UserSerializer
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
