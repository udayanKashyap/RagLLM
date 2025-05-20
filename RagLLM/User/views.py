from rest_framework.views import APIView, Response
from django.shortcuts import render
from rest_framework import status, permissions
from .serializers import UserSerializer
from .models import User


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
